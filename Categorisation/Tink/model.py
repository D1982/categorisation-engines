"""Facade to the core categorisation process offered by Tink.

The model implementation represents a kind of MVP Tink client application.
"""

import Categorisation.Tink.api as api

import logging
import os
import sys

from enum import Enum


""" The model class is a facade for the functionality typically required in a PoC.

All methods within this class should only be invoked by either instances of ui.TinkUI or by instas of 
this class (model.TinkModel) itself.
Communication with the UI does happen by returning the summarized logs which the UI can then 
print appropriately to the output.
"""


class TinkModel:

    def __init__(self, dao):
        """
        Initialization.

        :param dao: Reference to an instance of the class data.TinkDAO.
        """
        # Data Access Object
        self.dao = dao
        self.ui = None

        # Settings (will be set by instances of class TinkUI)
        self.delete_flag = False  # Flag whether to pre-delete existing data
        self.proxy_usage_flag = False  # Flag whether to use a http proxy

        # Variables
        self.token_type = ''
        self.expires_in = ''
        self.access_token = ''
        self.refresh_token = ''
        self.scope = ''
        self.id_hint = ''
        self.code = ''

    """Read user test data from files."""
    def read_user_data(self):
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        data = self.dao.read_users()
        if data:
            result_status = TinkModelResultStatus.Success
        else:
            result_status = TinkModelResultStatus.Error

        return TinkModelResult(result_status, data)

    """Read account test data from files."""
    def read_account_data(self):
        data = self.dao.read_accounts()
        if data:
            result_status = TinkModelResultStatus.Success
        else:
            result_status = TinkModelResultStatus.Error

        return TinkModelResult(result_status, data)

    """Read transaction test data from files."""
    def read_transaction_data(self):
        data = self.dao.read_transactions()
        if data:
            result_status = TinkModelResultStatus.Success
        else:
            result_status = TinkModelResultStatus.Error

        return TinkModelResult(result_status, data)

    """Test the API connectivity."""
    def test_connectivity(self):
        """
        Test the API connectivity.

        :return: TinkModelMultiResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        service = api.MonitoringService()

        # Wrapper for the results
        result_list = list()

        # 1. Call the ping service
        response = service.ping()
        if response.response_orig.status_code == 200:
            status = TinkModelResultStatus.Success
        else:
            status = TinkModelResultStatus.Error
        result_list.append(TinkModelResult(status, response))

        # 2. Call the health check service
        response = service.health_check()
        if response.response_orig.status_code == 200:
            status = TinkModelResultStatus.Success
        else:
            status = TinkModelResultStatus.Error
        result_list.append(TinkModelResult(status, response))

        return TinkModelMultiResult(result_list)

    def authorize_client(self, grant_type='client_credentials', scope='authorization:grant'):
        """
        Authorize the client (Tink customer account).

        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials
        :param scope: the requested scope when using client credentials.

        :return: TinkModelResult containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        service = api.OAuthService()
        response = service.authorize_client_access(grant_type=grant_type, scope=scope)

        logging.debug(response.request.to_string_formatted() + os.linesep + response.to_string_formatted())

        if response.status_code == 200:
            result_status = TinkModelResultStatus.Success
        else:
            result_status = TinkModelResultStatus.Error

        return TinkModelResult(result_status, response)

    def authorize_client_delete(self, grant_type='client_credentials', scope='user:delete', delete_dict=None):
        """
        Authorize the client (Tink customer account) to delete an object in the Tink platform.

        Wrapper for the API endpoint /api/v1/oauth/token
        This is to be considered as a workaround resp. the only way to delete an existing user.

        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials
        :param scope: the requested scope when using client credentials.
        :param delete_dict: If delete_dict is provided then the service has to be used to delete data.
        This is a workaround that can be used in order to delete existing users and accounts

        :return: TinkModelResult containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        if not delete_dict:
            msg = 'Parameter delete_dict was expected to be provided'
            logging.error(msg)
            raise Exception(args=msg)

        if 'user_id' in delete_dict:
            key = 'user_id'
            value = delete_dict[key]
        elif 'ext_user_id' in delete_dict:
            key = 'ext_user_id'
            value = delete_dict[key]
        else:
            msg = 'Unexpected keys in parameter delete_dict found'
            logging.error(msg)
            raise Exception(msg)
        # TODO: Add here the account_id in case of deletion for accounts is also working

        msg = 'Trying to authorize deletion of {k}:{v} '.format(k=key, v=value)
        logging.debug(msg)
        self.ui.put_result_log(msg, False)

        s = api.OAuthService()
        response = s.authorize_client_access(grant_type, scope, delete_dict)

        if response.status_code in (200, 204):
            logging.info('Successfully authorized deletion of {k}:{v} '.format(k=key, v=value))
            result_status = TinkModelResultStatus.Success

        elif response.status_code == 404:
            logging.warning('Object does not exist - {k}:{v} '.format(k=key, v=value))
            result_status = TinkModelResultStatus.Warning

        return TinkModelResult(result_status, response)

    def grant_user_access(self, client_access_token, ext_user_id, scope):
        """
        Grant an access code to perform an action that was previously authorized.

        Wrapper for the API endpoint /api/v1/oauth/authorization-grant

        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)
        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param scope: the requested scope when using client credentials.

        :return: TinkModelResult containing an instance of api.OAuth2AuthorizeResponse with an
        authorization code {CODE}.
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        service = api.OAuthService()
        response = service.grant_user_access(client_access_token=client_access_token,
                                             ext_user_id=ext_user_id,
                                             scope=scope)

        if response.status_code == 200:
            self.code = response.data['code']
            msg = 'The authorization code for deletion of user "{u}" is "{c}"'.format(c=self.access_code,
                                                                                      u=ext_user_id)
            logging.debug(msg)
            self.ui.put_result_log(msg, False)
            result_status = TinkModelResultStatus.Success
        else:
            result_status = TinkModelResultStatus.Error

        return TinkModelResult(result_status, response)

    def get_oauth_access_token(self, code, grant_type):
        """
        Get the OAuth access token for the user to perform an action that was previously authorized.

        Wrapper for the API endpoint /api/v1/oauth/token

        :param code: the authorization code gathered via the endpoint /api/v1/oauth/token which can
        be called using OAuthService.grant_user_access(...)
        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials

        :return: TinkModelResult containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        service = api.OAuthService()
        response = service.get_oauth_access_token(code=code, grant_type=grant_type)

        if response.status_code == 200:
            msg = 'Successfully received access token {t} for code {c}'.format(t=self.access_token, c=code)
            logging.debug(msg)
            self.ui.put_result_log(msg, False)
            result_status = TinkModelResultStatus.Success
        else:
            msg = 'Error when trying to receive an access token {t} for code {c}'.format(t=self.access_token, c=code)
            logging.debug(msg)
            self.ui.put_result_log(msg, False)
            result_status = TinkModelResultStatus.Error

            return TinkModelMultiResult(response)

    def activate_user(self, ext_user_id, label, market, locale, client_access_token):
        """
        Create a new user in the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param label: description of the user like e.g. the name
        :param market: ISO country code like e.g. UK, DE, CH
        :param locale: ISO language code like e.g. en_US, en_GB, de_CH, fr_CH
        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        # Make sure that there is a valid client_access_token available
        if not client_access_token:
            result = self.authorize_client(scope='user:create')
            if result.status == TinkModelResultStatus.Success:
                client_access_token = result.response.data['access_token']

        service = api.UserService()
        response = service.activate_user(ext_user_id, label, market, locale, client_access_token)

        if response.content and response.status_code == 204:
            result_status = TinkModelResultStatus.Success
            msg = 'Response from {dest} => {data}'.format(dest=response.request.endpoint,
                                                          data=str(response.to_string()))
            logging.debug(msg)
            self.ui.put_result_log(msg, False)
        else:
            result_status = TinkModelResultStatus.Success
            msg = 'Response from {dest} not as expected => {data}'.format(dest=response.request.endpoint,
                                                                          data=str(response.to_string()))
            logging.debug(msg)
            self.ui.put_result_log(msg, False)

        return TinkModelResult(result_status, response)

    def activate_users(self):
        """
        Initiates the creation of multiple users in the Tink platform.

        Reads users from a DAO, gets an access token from Tink's API and creates all users
        Hints:
        1. At the moment there is only one authentication step meaning if the token
        would expire due to longer runtime the current implementation would fail.
        2. It is clear that it would be more efficient to use one single API wrapper

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        # Get user data
        users = self.dao.read_users()

        # Wrapper for the results
        result_list = list()

        # Authorize client to create users
        result = self.authorize_client(grant_type='client_credentials', scope='user:create')
        result_list.append(result)

        if result.status == TinkModelResult.success:
            for e in users:
                ext_user_id = e['external_user_id']
                label = e['label']
                market = e['market']
                locale = e['locale']
                # Create the user
                result = self.activate_user(ext_user_id, label, market, locale, self.access_token)
                result_list.append(result)

        return TinkModelMultiResult(result_list)

    def user_exists(self, user_id=None, ext_user_id=None):
        """
        Checks if a user does already exist in the Tink platform.
        :param user_id: the unique Tink user identifier
        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :return: Boolean - True if the user exists, otherwise False
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        if user_id:  # TODO: Create a function to encapsulate delete_dict evaluation
            delete_dict = {'user_id': user_id}
        elif ext_user_id:
            delete_dict = {'external_user_id': user_id}

        # Authorize client to delete users
        result = self.authorize_client_delete(grant_type='client_credentials',
                                              scope='user:delete',
                                              delete_dict=delete_dict)

        if result.response == 204:
            return True  # User exists
        elif result.response == 404:
            return False  # User does not exist

    def delete_user(self, user_id=None, ext_user_id=None):
        """
        "Delete a user in the Tink platform.

        :param user_id: The unique Tink user identifier
        :param ext_user_id: external user reference (this is NOT the Tink internal id)

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        # TODO: Refactor Code
        # Prepare a dictionary that contains the user to be deleted
        if user_id:  # TODO: Create a function to encapsulate delete_dict evaluation
            key = 'user_id'
            value = user_id
        elif ext_user_id:
            key = 'ext_user_id'
            value = ext_user_id

        delete_dict = {key: value}

        # Wrapper for the results
        result_list = list()

        # --- 1. Authorize client
        msg = '1.Authorize client to delete the user {k}:{v}...'.format(k=key, v=value)
        logging.debug(msg)
        self.ui.put_result_log(text=msg, clear=False)
        try:
            result = self.authorize_client_delete(scope='user:delete', delete_dict=delete_dict)
        except Exception as e:
            logging.debug(e)
            dummy_response = api.OAuth2AuthenticationTokenResponse(None, None)
            return TinkModelResult(TinkModelResultStatus.Error, dummy_response)
        response: api.OAuth2AuthenticationTokenResponse = result.response

        if response.status == 200:
            result_status = TinkModelResultStatus.Success
            client_access_token = response.client_access_token
        else:
            result_status = TinkModelResultStatus.Error

        result_list.append(TinkModelResult(result_status, response))

        # --- Grant access and get the access code
        msg = '2.Grant access to the user to delete the user {k}:{v}...'.format(k=key, v=value)
        logging.debug(msg)
        self.ui.put_result_log(text=msg, clear=False)
        result = self.grant_user_access(client_access_token=client_access_token,
                                        ext_user_id=value,
                                        scope='user:delete')
        response: api.OAuth2AuthorizeResponse = result.response

        if response.status == 200:
            result_status = TinkModelResultStatus.Success
            code = response.code
        else:
            result_status = TinkModelResultStatus.Error

        msg = response.request.to_string_formatted() + response.to_string_formatted()
        self.ui.put_result_log(text=msg, clear=False)
        result_list.append(TinkModelResult(result_status, response))
        
        # --- 3. Get the OAuth access token to delete a user
        msg = '3.Get the OAuth access token to delete the user {k}:{v}...'.format(k=key, v=value)
        logging.debug(msg)
        self.ui.put_result_log(text=msg, clear=False)

        result = self.get_oauth_access_token(code=code, grant_type='authorization_code')
        response: api.OAuth2AuthenticationTokenResponse = result.response

        if response.status == 200:
            result_status = TinkModelResultStatus.Success
            access_token = response.access_token
        else:
            result_status = TinkModelResultStatus.Error

        msg = response.request.to_string_formatted() + response.to_string_formatted()
        self.ui.put_result_log(text=msg, clear=False)
        result_list.append(TinkModelResult(result_status, response))

        # 4. --- Delete the  user
        msg = '4.Delete the user {k}:{v}...'.format(k=key, v=value)
        logging.debug(msg)
        self.ui.put_result_log(msg)
        service = api.UserService()
        result = service.delete_user(access_token=access_token)
        response: api.UserDeleteResponse = result.response

        if response.status == 204:
            result_status = TinkModelResultStatus.Success
            deleted_user_id = response.user_id
            logging.debug('User {k}: {v} deleted (user_id:{u}'.format(k=key, v=value, u=deleted_user_id))
        else:
            result_status = TinkModelResultStatus.Error

        msg = response.request.to_string_formatted() + response.to_string_formatted()
        self.ui.put_result_log(text=msg, clear=False)
        result_list.append(TinkModelResult(result_status, response))

        return TinkModelMultiResult(result_list)

    def delete_users(self):
        """
        "Delete users in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        # Get user data
        users = self.dao.read_users()

        # Wrapper for the results
        result_list = list()

        # Delete existing users
        for e in users:
            # Delete user
            key = 'external_user_id'
            msg = 'Trying to delete user {k}: {v}...'.format(k=key, v=e[key])
            self.ui.put_result_log(text=msg, clear=False)
            result = self.delete_user(ext_user_id=e[key])
            self.ui.put_result_log('...' + result.status.value)
            result_list.append(result)

        return TinkModelMultiResult(result_list)

    def ingest_accounts(self):
        """
        Initiates the ingestion of accounts in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        result_log = ''
        return result_log

    def delete_accounts(self):
        """
        Initiates the deletion of accounts in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        result_log = ''
        return result_log

    def list_accounts(self):
        """
        Initiates the retrieval of a list of all accounts in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        result_log = ''
        return result_log

    def ingest_trx(self):
        """
        Initiates the ingestion of transactions in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        result_log = ''
        return result_log

    def delete_trx(self):
        """
        Initiates the deletion of transactions in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        result_log = ''
        return result_log

    def list_trx(self):
        """
        Initiates the retrieval of a list of all transactions in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        result_log = ''
        return result_log

    def process(self):
        """
        Process the full PoC pipeline.

        Delete users (if the corresponding checkbutton is set)
        Create users
        Delete accounts (if the corresponding checkbutton is set)
        Ingest accounts
        Ingest transactions

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        result_log = ''
        return result_log

        # Check if pre-delete is allowed)
        if not self.delete_flag:
            msg = 'Pre-Delete skipped: Deletion of existing objects in the Tink platform is disabled.'
            logging.info(msg)
        else:
            msg = 'Pre-Delete enabled: Existing objects in the Tink platform will be deleted.'
            logging.info(msg)
            result_log += os.linesep + msg + os.linesep
            # If yes: Delete the users
            result_log += self.delete_users()

        # Re-Create users
        result_log += self.activate_users()

        return result_log

    def list_categories(self):
        """
        Get a list of all categories in the Tink platform.

        :return: TinkModelResult
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        service = api.CategoryService()
        response = service.list_categories()

        if response.response_orig.status_code == 200:
            status = TinkModelResultStatus.Success
        else:
            status = TinkModelResultStatus.Error

        return TinkModelResult(status, response)

"""Enumeration for an overall status of an action performed in the Tink platform."""

class TinkModelResultStatus(Enum):
    Undefined = 'Status has not yet been set'
    Success = 'Successfully completed'
    Error = 'Completed with errors'
    Warning = 'Completed with warning'
    Stopped = 'Stopped due to an unexpected error'


"""Wrapper for the result of an action performed in the Tink platform."""


class TinkModelResult:

    def __init__(self, status=TinkModelResultStatus.Undefined, response: api.TinkAPIResponse=None):
        """
        Initialization.

        :param status: Reference to an instance of the Enum class TinkResultStatus.
        :param data: Reference to an instance of a sub-class of the class api.TinkAPIResponse.
        """
        self.status = status
        self.response = response


"""Wrapper for the results of multiple actions performed in the Tink platform."""


class TinkModelMultiResult:
    # TODO: Should also support containing TinkModelMultiResult (see delete_users->delete_user)
    def __init__(self, results=None):
        """
        Initialization.

        :param results: Reference to a list of instances of class TinkModelResult
        list[api.TinkAPIResponse].
        """
        if results and isinstance(results, list):
            self.results = results
        else:
            self.results = list()
            self.results.append(TinkModelResult())

        if self.count(TinkModelResultStatus.Success) == len(self.results):
            self.status = TinkModelResultStatus.Success
        else:
            self.status = TinkModelResultStatus.Warning

    def count(self, status: TinkModelResultStatus):
        """
        :param status: Reference to an instance of the Enum class TinkResultStatus.

        :return: The number of elements in the list self.result with the requested status
        """
        cnt = sum(e.status == status for e in self.results)

        return cnt

"""
Selection of Tink scopes.

categories:read
accounts:read
contacts:read
credentials:read
documents:read
follow:read
statistics:read
suggestions:read
properties:read
providers:read
investments:read
authorization:grant
user:create
user:read
user:delete
user:web_hooks
credentials:write
credentials:refresh
transactions:read
transactions:categorize
transactions:write
"""
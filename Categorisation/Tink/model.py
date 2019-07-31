"""Facade to the core categorisation process offered by Tink.

The model implementation represents a kind of MVP Tink client application.
"""
import Categorisation.Common.exceptions as ex
import Categorisation.Common.config as cfg
import Categorisation.Common.util as utl
import Categorisation.Tink.api as api
import Categorisation.Tink.data as data


import logging
import os
import sys
import collections

from enum import Enum


class TinkModel:

    """
    The model class is a facade for the functionality typically required in a PoC.

    All methods within this class should only be invoked by either instances of ui.TinkUI or by instas of
    this class (model.TinkModel) itself.
    Communication with the UI does happen by returning the summarized logs which the UI can then
    print appropriately to the output.
    """

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
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        return self.dao.read_users()


    """Read account test data from files."""
    def read_account_data(self):
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        return self.dao.read_accounts()

    """Read transaction test data from files."""
    def read_transaction_data(self):
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        return self.dao.read_transactions()

    """Test the API connectivity."""
    def test_connectivity(self):
        """
        Test the API connectivity.

        :return: TinkModelResultList wrapping TinkModelResult objects of all AP calls performed
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        service = api.MonitoringService()

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action=msg, msg='Test API connectivity')

        # 1. Call the ping service
        response = service.ping()
        if response.status_code == 200:
            status = TinkModelResultStatus.Success
        else:
            logging.error(response.summary())
            status = TinkModelResultStatus.Error
        result_list.append(TinkModelResult(status, response, 'Ping'))

        # 2. Call the health check service
        response = service.health_check()
        if response.status_code == 200:
            status = TinkModelResultStatus.Success
        else:
            logging.error(response.summary())
            status = TinkModelResultStatus.Error
        result_list.append(TinkModelResult(status, response, 'Health check'))

        return result_list

    def authorize_client(self, grant_type='client_credentials', scope='authorization:grant'):
        """
        Authorize the client (Tink customer account).

        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials
        :param scope: the requested scope when using client credentials.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        service = api.OAuthService()
        response = service.authorize_client_access(grant_type=grant_type, scope=scope)

        if response.status_code == 200:
            logging.info('Authorized client access')
            logging.info('Client access token: {t}'.format(t=response.access_token))
            result_status = TinkModelResultStatus.Success
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        return TinkModelResultList(TinkModelResult(result_status, response, ''))

    def authorize_client_delete(self, grant_type='client_credentials', scope='user:delete', delete_dict=None):
        """
        Authorize the client (Tink customer account) to delete an object in the Tink platform.

        Wrapper for the API endpoint /api/v1/oauth/token
        This is to be considered as a workaround resp. the only way to delete an existing user.

        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials
        :param scope: the requested scope when using client credentials.
        :param delete_dict: If delete_dict is provided then the service has to be used to delete data.
        This is a workaround that can be used in order to delete existing users and accounts

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        if not delete_dict:
            msg = 'Parameter delete_dict was expected to be provided'
            logging.error(msg)
            raise Exception(msg)

        if 'user_id' in delete_dict:
            key = 'user_id'
            value = delete_dict[key]
        elif 'ext_user_id' in delete_dict:
            key = 'ext_user_id'
            value = delete_dict[key]
        else:
            msg = 'Unexpected keys in parameter delete_dict found'
            logging.error(msg)
            raise ex.ParameterError(msg)
        # TODO: Add here the account_id in case of deletion for accounts is also working

        s = api.OAuthService()
        response = s.authorize_client_access(grant_type, scope, delete_dict)

        if response.status_code in (200, 204):
            logging.info('Authorized client access for deletion of {k}:{v} '.format(k=key, v=value))
            result_status = TinkModelResultStatus.Success
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        return TinkModelResultList(TinkModelResult(result_status, response, ''))

    def grant_user_access(self, client_access_token, ext_user_id, scope):
        """
        Grant an access code to perform an action that was previously authorized.

        Wrapper for the API endpoint /api/v1/oauth/authorization-grant

        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)
        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param scope: the requested scope when using client credentials.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.OAuth2AuthorizeResponse with an authorization code {CODE}.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        service = api.OAuthService()
        response = service.grant_user_access(client_access_token=client_access_token,
                                             ext_user_id=ext_user_id,
                                             scope=scope)

        response: api.OAuth2AuthorizeResponse = response
        if response.status_code == 200:
            code = response.data['code']
            msg = 'Received access code "{c}"'.format(c=code)
            logging.info(msg)
            result_status = TinkModelResultStatus.Success
        elif response.status_code == 404:
            # User does not exist
            text = 'User ext_user_id:{u} does not exist'.format(u=ext_user_id)
            logging.warning(text)
            result_status = TinkModelResultStatus.Exception
            rl = TinkModelResultList(TinkModelResult(status=result_status,
                                                     response=response,
                                                     action='Grant user access',
                                                     msg=text))
            raise ex.UserNotExistingError(text, rl)
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        return TinkModelResultList(TinkModelResult(result_status, response, ''))

    def get_oauth_access_token(self, code, grant_type):
        """
        Get the OAuth access token for the user to perform an action that was previously authorized.

        Wrapper for the API endpoint /api/v1/oauth/token

        :param code: the authorization code gathered via the endpoint /api/v1/oauth/token which can
        be called using OAuthService.grant_user_access(...)
        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        service = api.OAuthService()
        response = service.get_oauth_access_token(code=code, grant_type=grant_type)

        if response.status_code == 200:
            msg = 'Got access_token:{t} using code:{c}'.format(t=response.access_token, c=code)
            logging.info(msg)
            result_status = TinkModelResultStatus.Success
        else:
            logging.debug(response.summary())
            result_status = TinkModelResultStatus.Error

        return TinkModelResultList(TinkModelResult(result_status, response, ''))

    def activate_user(self, ext_user_id, label, market, locale, client_access_token):
        """
        Create a new user in the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param label: description of the user like e.g. the name
        :param market: ISO country code like e.g. UK, DE, CH
        :param locale: ISO language code like e.g. en_US, en_GB, de_CH, fr_CH
        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.UserActivationResponse with a unique identifier of
        the user created {USER_ID}.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Wrapper for the results
        msg = 'Create (activate) user ext_user_id:{e}'.format(e=ext_user_id)
        result_list = TinkModelResultList(result=None, action=msg, msg=msg)

        # Make sure that there is a valid client_access_token available
        if not client_access_token:
            # --- Authorize client
            rl = self.authorize_client(scope='authorization:grant,user:create')
            response: api.OAuth2AuthenticationTokenResponse = rl.first().response

            # TODO: Refactor using TinkModelResultList pattern (see ingest_accounts)
            if response.status_code == 200:
                result_status = TinkModelResultStatus.Success
                client_access_token = response.access_token
            else:
                logging.error(response.summary())
                result_status = TinkModelResultStatus.Error

            # Results
            result = TinkModelResult(status=result_status,
                                     response=response,
                                     action='Authorize client',
                                     msg=result_status.value)

            result_list.append(result)

        # --- Create user
        service = api.UserService()
        response = service.activate_user(ext_user_id, label, market, locale, client_access_token)

        if response.status_code == 200:
            result_status = TinkModelResultStatus.Success
            user_id = response.user_id
            msg = 'User with ext_user_id:{e} created as user_id:{u}'.format(e=ext_user_id,
                                                                            u=user_id)
            logging.info(msg)
        elif response.status_code == 409:
            result_status = TinkModelResultStatus.Warning
            msg = 'User with ext_user_id:{e} does already exist'.format(e=ext_user_id)
            logging.info(msg)
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        # Results
        result = TinkModelResult(status=result_status,
                                 response=response,
                                 action='Create user ext_user_id:{e}'.format(e=ext_user_id),
                                 msg=result_status.value)

        result_list.append(result)

        return result_list

    def activate_users(self):
        """
        Initiates the creation of multiple users in the Tink platform.

        Reads users from a DAO, gets an access token from Tink's API and creates all users
        Hints:
        1. At the moment there is only one authentication step meaning if the token
        would expire due to longer runtime the current implementation would fail.
        2. It is clear that it would be more efficient to use one single API wrapper

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing instances of api.UserActivationResponse with a unique identifier of
        the users deleted {USER_ID}.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Get user data
        users = self.dao.read_users()

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action=msg, msg='Activate users')

        if users:
            for e in users:
                # Get user attributes
                ext_user_id = e['userExternalId']
                label = e['label']
                market = e['market']
                locale = e['locale']

                # Create the user
                rl = self.activate_user(ext_user_id, label, market, locale, self.access_token)
                result_list.append(rl)

        return result_list

    def user_exists(self, ext_user_id):
        """
        Checks if a user does already exist in the Tink platform.
        :param user_id: the unique Tink user identifier
        :param ext_user_id: external user reference (this is NOT the Tink internal id)

        :return: Boolean - True if the user exists, otherwise False
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)
        try:
            self.delete_user(ext_user_id=ext_user_id, no_delete=True)
        except ex.UserNotExistingError as e:
            logging.debug(e.text)
            # If the exception ExUserNotExisting is being raised the user does not exist
            return False

        # If the exception ExUserNotExisting was NOT then the user does
        # exist and could be deleted with delete_user( ...  no_delete = False)
        return True

    def delete_user(self, user_id=None, ext_user_id=None, no_delete=False):
        """
        "Delete a user in the Tink platform.

        Hint: The parameter no_delete makes sense to not duplicate code since the
        handling of user deletion in the Tink platform is very special for whatever
        reason. Therefore the method model.user_exists() makes use of this parameter in
        order to verify if a user exists.

        :param user_id: The unique Tink user identifier
        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param no_delete: Flag to suppress user deletion e.g. in order to only check if the user
        is existing in the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.UserDeleteResponse with a unique identifier of
        the user deleted {USER_ID}.

        :raise: ExUserNotExisting in case the user to be deleted does not exist
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(msg)

        # Prepare a dictionary that contains the user to be deleted
        if user_id:  # TODO: Create a function to encapsulate delete_dict evaluation
            key = 'user_id'
            value = user_id
        elif ext_user_id:
            key = 'ext_user_id'
            value = ext_user_id

        delete_dict = {key: value}

        # Wrapper for the results
        msg = 'Delete user with ext_user_id:{e}'.format(e=ext_user_id)
        result_list = TinkModelResultList(result=None, action=msg, msg=msg)

        msg = 'Authorize client...'.format(k=key, v=value)
        try:
            rl = self.authorize_client_delete(scope='authorization:grant,user:delete',
                                              delete_dict=delete_dict)
            result_list.append(rl)
        except ex.ParameterError as e:
            raise e

        if rl.last().status == TinkModelResultStatus.Success:
            response: api.OAuth2AuthenticationTokenResponse = rl.last().response
            client_access_token = response.access_token
            logging.info(msg + ' => client_access_token:{t}'.format(t=client_access_token))
            result_list.append(rl)
        else:
            logging.error(rl.last().response.summary())

        msg = 'Grant access and get the access code...'
        try:
            rl = self.grant_user_access(client_access_token=client_access_token,
                                        ext_user_id=value,
                                        scope='user:delete')
            result_list.append(rl)
        except ex.UserNotExistingError as e:
            raise e

        if rl.last().status == TinkModelResultStatus.Success:
            response: api.OAuth2AuthorizeResponse = rl.last().response
            code = response.code
            logging.debug(msg + ' => code:{c}'.format(c=code))

            if no_delete:
                # Delete is suppressed and therefore we can also stop here
                # even if the user exists and could in theory be deleted
                return TinkModelResultList(result_list)
        else:
            logging.error(response.summary())

        msg = 'Get the OAuth access token to delete a user...'
        rl = self.get_oauth_access_token(code=code, grant_type='authorization_code')
        result_list.append(rl)

        if rl.last().status == TinkModelResultStatus.Success:
            response: api.OAuth2AuthenticationTokenResponse = rl.last().response
            access_token = response.access_token
            logging.info(msg + ' => access_token:{t}'.format(t=access_token))
        else:
            logging.error(response.summary())

        msg = 'Delete user ext_user_id:{e}'.format(e=ext_user_id)
        service = api.UserService()
        response: api.UserDeleteResponse = service.delete_user(access_token=access_token)

        if response.status_code in (200, 204):
            result_status = TinkModelResultStatus.Success
            logging.info(msg + ' => ext_user_id:{u} deleted'.format(u=ext_user_id))
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        result_list.append(TinkModelResult(result_status, response, msg))

        return result_list

    def delete_users(self):
        """
        "Delete users in the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing instances of api.UserDeleteResponse with a unique identifier of
        the users deleted {USER_ID}.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Get user data
        users = self.dao.read_users()

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action=msg, msg='Delete users')

        # Delete existing users
        key = 'userExternalId'
        for e in users:
            if isinstance(e, collections.OrderedDict):
                if key in e:
                    # Delete user
                    msg = 'Delete user {k}:{v}...'.format(k=key, v=e[key])
                    try:
                        rl = self.delete_user(ext_user_id=e[key])
                        result_list.append(rl)
                    except ex.UserNotExistingError as e:
                        result_list.append(e.result_list)

        return result_list

    def ingest_accounts(self):
        """
        Initiates the ingestion of accounts in the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing instances of api.AccountIngestionResponse with a status code:
        STATUS CODE	DESCRIPTION
        204	Accounts created.
        400	The payload does not pass validation.
        401	User not found, has no credentials, or has more than one set of credentials.
        409	Account already exists.
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Get account data
        accounts_raw = self.dao.read_accounts()
        accounts = data.TinkAccountList(accounts_raw)

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action=msg, msg='Ingest accounts')

        try:
            accounts: data.TinkAccountList(accounts_raw)
        except AttributeError as e:
            logging.debug(e)
            raise e

        service = api.AccoungService()
        users = self.dao.read_users()

        # --- Authorize client
        rl = self.authorize_client(scope='authorization:grant,accounts:write')
        response: api.OAuth2AuthenticationTokenResponse = rl.last().response

        # TODO: Refactor using standard pattern (see ingest_accounts)
        if rl.status() == TinkModelResultStatus.Success:
            client_access_token = response.access_token
        else:
            logging.error(response.summary())

        result_list.append(rl)

        # --- Ingest accounts per user
        if users:
            for e in users:
                # Get user attributes
                ext_user_id = e['userExternalId']
                user_accounts = accounts.get_data(ext_user_id)
                rl = service.ingest_accounts(ext_user_id=ext_user_id,
                                             accounts=user_accounts,
                                             client_access_token=client_access_token)
                result_list.append(rl)

        return result_list

    def delete_accounts(self):
        """
        Initiates the deletion of accounts in the Tink platform.

        :return: TinkModelResult
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(msg='')

        return result_list

    def list_accounts(self):
        """
        Initiates the retrieval of a list of all accounts in the Tink platform.

        :return: TinkModelResult
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList

        return result_list

    def ingest_trx(self):
        """
        Initiates the ingestion of transactions in the Tink platform.

        :return: TinkModelResult
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(msg='')

        return result_list

    def delete_trx(self):
        """
        Initiates the deletion of transactions in the Tink platform.

        :return: TinkModelResult
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(msg='')

        return result_list

    def list_trx(self):
        """
        Initiates the retrieval of a list of all transactions in the Tink platform.

        :return: TinkModelResult
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(msg='')

        return result_list

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
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(msg='')

        # Check if pre-delete is allowed)
        if self.delete_flag is True:
            msg = 'Pre-Delete enabled: Existing objects in the Tink platform will be deleted.'
            logging.info(msg)
            # If yes: Delete the users
            rl = self.delete_users()
            result_list.append(rl)
        else:
            msg = 'Pre-Delete skipped: Deletion of existing objects in the Tink platform is disabled.'
            logging.info(msg)

        # Re-Create users
        rl = self.activate_users()
        result_list.append(rl)

        return result_list

    def list_categories(self):
        """
        Get a list of all categories in the Tink platform.

        :return: TinkModelResultList
        """
        msg = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.info(msg)

        service = api.CategoryService()
        response = service.list_categories()

        if response.status_code == 200:
            status = TinkModelResultStatus.Success
        else:
            status = TinkModelResultStatus.Error

        return TinkModelResultList(TinkModelResult(status, response, ''))


class TinkModelResultStatus(Enum):

    """
    Enumeration for an overall status of an action performed in the Tink platform.
    """

    Success = 'Successfully completed'
    Warning = 'Completed with warning'
    Error = 'Completed with errors'
    Exception = 'Stopped by an exception'
    Undefined = 'Status has not yet been set'


class TinkModelResult:

    """
    Wrapper for the result of an action performed in the Tink platform.
    """

    def __init__(self,
                 status=TinkModelResultStatus.Undefined,
                 response: api.TinkAPIResponse = api.DummyResponse(),
                 action: str = '',
                 msg: str = ''):
        """
        Initialization.

        :param status: Reference to an instance of the Enum class TinkResultStatus.
        :param response: Reference to an instance of a sub-class of the class api.TinkAPIResponse.
        :param action: a description of the action performed.
        :param msg: a message describing the main activity performed.
        """
        self.status = status
        self.response = response


        self.action = action
        if self.action == '':
            self.action = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)

        self.msg = msg

    def get(self, key):
        """
        Get a value from the dictionary self.data in case of existence.

        :param key: key for the dictionary lookup
        :return: the value if there could one be found in the dictionary
        """
        if key in self.response.data:
            return self.response.data[key]
        else:
            return ''


class TinkModelResultList:

    """
    Wrapper for the results of multiple actions performed in the Tink platform.
    """

    def __init__(self, result: TinkModelResult = None, action: str = '', msg: str = ''):
        """
        Initialization.

        :param result: Reference to an instance of class TinkModelResult - The first result
        to be appended to the list of result items.
        :param action: a description of the action performed.
        :param msg: a message describing the main activity performed.

        """
        self.results: list[TinkModelResult] = list()

        self.action = action
        if self.action == '':
            self.action = '{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)

        self.msg = msg

        # If provided save a list containing the initial result items
        if isinstance(result, TinkModelResult):
            self.results.append(result)
        else:
            logging.debug('Parameter "result" was ignored since it was not of expected type TinkModelResult')

    def status(self):
        """
        Gather the overall status over all result items in the list result_list
        Current ruleset:
        - If all items have status TinkModelResult.Success then this is also the overall status
        - If there exist items having status other than TinkModelResult.Success then the
        overall status is TinkModelResult.Warning

        :return: A value of the enum class TinkModelResultStatus
        """
        # Gather overall status over all result items
        if self.count(TinkModelResultStatus.Success) == len(self.results):
            overall_status = TinkModelResultStatus.Success
        else:
            overall_status = TinkModelResultStatus.Warning

        return overall_status

    def append(self, result: TinkModelResult):
        """
        Appends a new result item to the internal list result_items.
        :param result: a result item of type TinkModelResult to be added to the list
        :return: void
        """
        if isinstance(result, TinkModelResult):
            self.results.append(result)
        elif isinstance(result, TinkModelResultList):
            merged_list = self.results + result.results
            self.results = merged_list

    def first(self):
        """
        Get the first element in the internal list of result items
        :return: TinkModelResult
        """
        if len(self.results) > 0:
            return self.results[0]
        else:
            return TinkModelResult('Unbound')

    def last(self):
        """
        Get the last element in the internal list of result items
        :return: TinkModelResult
        """
        length = len(self.results)
        if length > 0:
            return self.results[length - 1]
        else:
            return TinkModelResult('Unbound')

    def get_elements(self, endpoint_filter: str = '/api/v1/'):
        """
        Get the latest TinkModelResult object in the list result_items for which the
        given string filter applies

        :param endpoint_filter: the substring for which a matching endpoint should be found

        :return: a list of TinkModelResult objects matching the endpoint_filter search string
        """
        lst = list()
        for e in self.results:
            if e.response.request.endpoint.find(endpoint_filter) != -1:  # Found
                lst.append(e)
            # Exceptions should 1) have this status set and 2) always be shown
            elif e.status == TinkModelResultStatus.Exception:
                lst.append(e)
        return lst

    def get_element(self, index=None, endpoint_filter: str = '/api/v1/'):
        """
        Get the all TinkModelResult objects in the list result_items for which the
        given string filter applies

        :param index: The exact list index of the element, if known
        :param endpoint_filter: the substring for which a matching endpoint should be found

        :return: The latest TinkModelResult object matching the endpoint_filter search string
        """
        if index and len(self.results) < index:
            return self.results[index]
        else:
            for e in self.results:
                if e.response.request.endpoint.find(endpoint_filter):
                    result = e
            return result  # Which is automatically the latest element

    def count(self, status: TinkModelResultStatus):
        """
        Count all elements having the given status.

        :param status: Reference to an instance of the Enum class TinkResultStatus.

        :return: The number of elements in the list self.result with the requested status
        """
        cnt = sum(e.status == status for e in self.results)

        return cnt

    def statistics(self):
        """
        Print statistics describing the overall status over all elements
        If at least one element does not have set TinkModelResultStatus.Success
        then the overall status will be TinkModelResultStatus.Warning

        :return: text containing statistics about all the result items contained
        """
        text = ''
        index = 0
        sep = ''
        for s in TinkModelResultStatus:
            index += 1
            # print(s.value)
            cnt = self.count(s)
            if cnt != 0:
                if index > 1:
                    sep = ', '
                text += sep + '{cnt}/{t} steps: {s}'.format(cnt=cnt, t=len(self.results), s=str(s.value))

        return text

    def summary(self, filters: dict() = None):
        """
        Print a summary including the outcome of all contained result items.
        The main purpose of this method is to provide an easy to use interface in order
        to print the results in a human-readable way on the user interface.

        :param filters: dictionary with filters to be applied to the results

        :return: Union of all responses wrapped into the result items as formatted text.
        """
        # Check Parameters
        if filters:
            for k, v in filters.items():
                if k == 'endpoint':
                    endpoint_filter = filters[k]
        else:
            endpoint_filter = ''

        # Get level of detail currently set for ui logs
        level = utl.message_detail_level()

        # Overall status over all results wrapped within this result list
        text = '{a} ... {s} [{m}]'.format(a=self.action, s=self.status().value, m=self.msg)

        # Overall statistics
        if level == cfg.MessageDetailLevel.High:
            text += os.linesep + self.statistics()
        else:
            logging.debug(self.statistics())

        # Reduce amount of results by using the provided filters
        if level == cfg.MessageDetailLevel.Low:
            # Print certain results only (of the list of actions performed)
            rl: list[TinkModelResult] = self.get_elements(endpoint_filter=endpoint_filter)
        else:
            rl = self.results

        # Summarize the status of the single steps
        if level == cfg.MessageDetailLevel.Low:
            for r in rl:
                text += os.linesep + '{a} ... {s}'.format(a=r.action, s=r.status.value)
                if r.msg and r.msg != r.status.value:
                    text += ' [{m}]'.format(m=r.msg)
                if r.response:
                    text += ' [{s}]'.format(s=r.response.summary())
        elif level == cfg.MessageDetailLevel.Medium:
            for i in range(len(self.results)):
                text += '\nResult #{i}\n{s}'.format(i=i + 1, s=self.results[i].response.summary())

        return text


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
"""Facade to the core categorisation process offered by Tink.

The model implementation represents a kind of MVP Tink client application.
"""
import Categorisation.Common.exceptions as ex
import Categorisation.Common.config as cfg
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

    def __init__(self, dao: data.TinkDAO):
        """
        Initialization.

        :param dao: Reference to an instance of the class data.TinkDAO.
        """
        self._dao = dao

        self._token_type = ''
        self._expires_in = ''
        self._client_access_token = ''
        self._access_token = ''
        self._refresh_token = ''
        self._scope = ''
        self._id_hint = ''
        self._code = ''

        # Define the supported actions that can be queried using the
        # corresponding property
        self._supported_actions = self._define_supported_actions()
        self._process_actions = self._define_process_actions()

    def _define_supported_actions(self):
        """
        TODO: Docstring

        :return:
        """
        methods = (self.test_connectivity, self.list_categories,
                   self.delete_users, self.activate_users, self.get_users,
                   self.ingest_accounts, self.get_all_accounts)

        actions = list()

        # Define supported actions
        for method in methods:
            action = {'method': method}
            filters = {}

            if method == self.test_connectivity:
                filters.update({'endpoints': []})
                action.update({'filters': filters})
            elif method == self.list_categories:
                filters.update({'endpoints': ['/categories']})
                action.update({'filters': filters})
            elif method == self.delete_users:
                filters.update({'endpoints': ['/user/delete']})
                action.update({'filters': filters})
            elif method == self.activate_users:
                filters.update({'endpoints': ['/user/delete', '/user/create']})
                action.update({'filters': filters})
            elif method == self.get_users:
                filters.update({'endpoints': ['/user']})
                action.update({'filters': filters})
            elif method == self.ingest_accounts:
                filters.update({'endpoints': ['/accounts']})
                action.update({'filters': filters})
            elif method == self.get_all_accounts:
                filters.update({'endpoints': ['/accounts/list']})
                action.update({'filters': filters})

            actions.append(action)

        return actions

    def _define_process_actions(self):
        """
        TODO: Docstring

        :return:
        """
        actions = list()

        excluded_actions = (self.test_connectivity, self.list_categories)

        for action in self._supported_actions:
            if action['method'] not in excluded_actions:
                actions.append(action)

        return actions

    @property
    def supported_actions(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._supported_actions

    @property
    def process_actions(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._process_actions

    def supported_action_filters(self, method):
        """
        Get the current output filter for a supported action (method reference).
        :return: The output filter for the supplied method reference.
        """
        for action in self._supported_actions:
            if action['method'] == method:
                filters = action['filters']
                return filters

        return None

    def save_data_to_file(self,
                          entity_type: cfg.EntityType,
                          fields: tuple,
                          locator,
                          payload: any):
        """
        Save
        Persists data for a valid entity over the DAO.
        :return: TinkModelResultList object.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        msg = f'Save results to "{locator}"'
        result = TinkModelResult(status=TinkModelResultStatus.Success,
                                 action=msg,
                                 msg='Done',
                                 is_important=True)

        # Check whether the payload delivered contains data
        if (isinstance(payload, list) and len(payload) > 0) or (isinstance(payload, dict) and len(payload.keys()) > 0):
            try:
                written_data = self._dao.data_access(entity_type=entity_type,
                                                     access_type=data.TinkDAO.WRITE,
                                                     locator=locator,
                                                     fields=fields,
                                                     payload=payload)

            except Exception as e:
                result.status = TinkModelResultStatus.Error
                result.msg = 'Failed'
                raise e
        else:
            result.msg = f'No data to write into a file: Payload {type(payload)} delivered was empty'

        logging.info(f'{result.action} => {result.msg}')

        return TinkModelResultList(result=result,
                                   action=result.action,
                                   msg=result.msg)

    def _oauth2_client_credentials_flow(self,
                                        grant_type,
                                        client_scope,
                                        user_scope,
                                        ext_user_id=None):
        """
        TODO: Docstring
        :param grant_type:
        :param client_scope:
        :param user_scope:
        :param ext_user_id:
        :return:
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        result_list = TinkModelResultList(result=None,
                                          action=msg,
                                          msg='OAuth client credentials access flow')

        msg = 'Authorize client...'
        rl = self._authorize_client(grant_type='client_credentials',
                                    scope=client_scope,
                                    ext_user_id=ext_user_id)
        result_list.append(rl)

        if rl.last().status == TinkModelResultStatus.Success:
            response: api.OAuth2AuthenticationTokenResponse = rl.last().response
            client_access_token = response.access_token
            self._client_access_token = client_access_token
            logging.info(msg + f' => client_access_token:{client_access_token}')
            result_list.append(rl)
        else:
            logging.error(rl.last().response.summary())

        msg = 'Grant access and get the access code...'
        try:
            rl = self._grant_user_access(client_access_token=client_access_token,
                                         ext_user_id=ext_user_id,
                                         scope=user_scope)
            result_list.append(rl)
        except ex.UserNotExistingError as e:
            raise e

        if rl.last().status == TinkModelResultStatus.Success:
            response: api.OAuth2AuthorizeResponse = rl.last().response
            code = response.code
            self._code = code
            logging.debug(msg + f' => code:{code}')
        else:
            logging.error(response.summary())

        msg = 'Get the OAuth access token to delete a user...'
        rl = self._get_oauth2_access_token(code=code, grant_type='authorization_code')
        result_list.append(rl)

        if rl.last().status == TinkModelResultStatus.Success:
            response: api.OAuth2AuthenticationTokenResponse = rl.last().response
            access_token = response.access_token
            self._access_token = access_token
            logging.info(msg + f' => access_token:{access_token}')
        else:
            logging.error(response.summary())

        return result_list

    def _authorize_client(self, grant_type='client_credentials', scope='authorization:grant', ext_user_id=None):
        """
        Authorize the client (Tink customer account).

        :param grant_type: the grant type.
        Possible values: authorization_code, refresh_token, client_credentials
        :param scope: the requested scope when using client credentials.
        Values: https://docs.tink.com/enterprise/api/#available-scopes
        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        This parameter can be used in order to delete existing users and accounts.
        This is a workaround suggested by Tink in order to delete a user-

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        service = api.OAuthService()
        if ext_user_id:
            response = service.authorize_client_access(grant_type=grant_type,
                                                       scope=scope,
                                                       ext_user_id=ext_user_id)
        else:
            response = service.authorize_client_access(grant_type=grant_type,
                                                       scope=scope)

        if response.http_status(cfg.HTTPStatusCode.Code2xx):
            logging.info('Authorized client access')
            logging.info(f'Client access token: {response.access_token}')
            result_status = TinkModelResultStatus.Success
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        return TinkModelResultList(TinkModelResult(result_status, response, ''))

    def _grant_user_access(self, client_access_token, ext_user_id, scope):
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
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        service = api.OAuthService()
        response = service.grant_user_access(client_access_token=client_access_token,
                                             ext_user_id=ext_user_id,
                                             scope=scope)

        response: api.OAuth2AuthorizeResponse = response
        if response.status_code == 200:
            code = response.data['code']
            msg = f'Received access code "{code}"'
            logging.info(msg)
            result_status = TinkModelResultStatus.Success
        elif response.status_code == 404:
            # User does not exist
            text = f'User ext_user_id:{ext_user_id} does not exist'
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

    def _get_oauth2_access_token(self, code, grant_type):
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
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        service = api.OAuthService()
        response = service.get_oauth_access_token(code=code, grant_type=grant_type)

        if response.status_code == 200:
            msg = f'Got access_token:{response.access_token} using code:{code}'
            logging.info(msg)
            result_status = TinkModelResultStatus.Success
        else:
            logging.debug(response.summary())
            result_status = TinkModelResultStatus.Error

        return TinkModelResultList(TinkModelResult(result_status, response, ''))

    def test_connectivity(self):
        """
        Test the API connectivity.

        :return: TinkModelResultList wrapping TinkModelResult objects of all AP calls performed
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
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
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # Wrapper for the results
        msg = f'Create (activate) user ext_user_id:{ext_user_id}'
        result_list = TinkModelResultList(result=None, action=msg, msg=msg)

        # Make sure that there is a valid client_access_token available
        if not client_access_token:
            # --- Authorize client
            rl = self._authorize_client(scope='authorization:grant,user:create')
            response: api.OAuth2AuthenticationTokenResponse = rl.first().response

            if response.http_status(cfg.HTTPStatusCode.Code2xx):
                result_status = TinkModelResultStatus.Success
                client_access_token = response.access_token
                self._client_access_token = client_access_token
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
            msg = f'User with ext_user_id:{ext_user_id} created as user_id:{user_id}'
            logging.info(msg)
        elif response.status_code == 409:
            result_status = TinkModelResultStatus.Warning
            msg = f'User with ext_user_id:{ext_user_id} does already exist'
            logging.info(msg)
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        # Results
        result = TinkModelResult(status=result_status,
                                 response=response,
                                 action=f'Create user ext_user_id:{ext_user_id}',
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
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        users = self._dao.users.data

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
                try:
                    # Delete user if exists
                    if cfg.TinkConfig.get_instance().delete_flag:
                        rl = self.delete_user(ext_user_id=ext_user_id)
                        result_list.append(rl)
                except ex.UserNotExistingError as e:
                    result_list.append(e.result_list)

                rl = self.activate_user(ext_user_id=ext_user_id,
                                        label=label,
                                        market=market,
                                        locale=locale,
                                        client_access_token=None)
                result_list.append(rl)

        return result_list

    def delete_user(self, ext_user_id=None, no_delete=False):
        """
        Delete a user in the Tink platform.

        Hint: The parameter no_delete makes sense to not duplicate code since the
        handling of user deletion in the Tink platform is very special for whatever
        reason. Therefore e.g. the method model.user_exists() makes use of this parameter in
        order to verify whether a user exists.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param no_delete: Flag to suppress user deletion e.g. in order to only check if the user
        is existing in the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.UserDeleteResponse with a unique identifier of
        the user deleted {USER_ID}.

        :raise ExUserNotExisting: in case the user to be deleted does not exist
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Wrapper for the results
        msg = f'Delete user with ext_user_id:{ext_user_id}'
        result_list = TinkModelResultList(result=None, action=msg, msg='')

        # Get the required OAuth2 access code
        try:
            rl = self._oauth2_client_credentials_flow(grant_type='client_credentials',
                                                      client_scope='authorization:grant,user:delete',
                                                      user_scope='user:delete',
                                                      ext_user_id=ext_user_id)
            result_list.append(rl)
        except ex.UserNotExistingError as e:
            raise e

        msg = f'Delete user ext_user_id:{ext_user_id}'
        service = api.UserService()
        response: api.UserDeleteResponse = service.delete_user(access_token=self._access_token)

        if response.http_status(cfg.HTTPStatusCode.Code2xx):
            result_status = TinkModelResultStatus.Success
            msg = f' => ext_user_id:{ext_user_id} deleted'
            logging.info(msg)
        else:
            result_status = TinkModelResultStatus.Error
            msg = f' => ext_user_id:{ext_user_id} could not be deleted'
            logging.error(response.summary())

        result_list.append(TinkModelResult(result_status, response, msg))

        return result_list

    def delete_users(self):
        """
        Delete users in the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing instances of api.UserDeleteResponse with a unique identifier of
        the users deleted {USER_ID}.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action='Delete Users', msg='')

        users = self._dao.users.data

        # Delete existing users
        key = 'userExternalId'
        for e in users:
            if isinstance(e, collections.OrderedDict):
                if key in e:
                    # Delete user
                    msg = f'Delete user {key}:{e[key]}...'
                    logging.info(msg)
                    try:
                        rl = self.delete_user(ext_user_id=e[key])
                        result_list.append(rl)
                    except ex.UserNotExistingError as e:
                        result_list.append(e.result_list)

        return result_list

    def get_user(self, ext_user_id=None):
        """
        Get the details of a user within the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.UserDeleteResponse with a unique identifier of
        the user deleted {USER_ID}.
        :raise ExUserNotExisting: in case the user to be deleted does not exist
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Wrapper for the results
        msg = f'Get information about user with ext_user_id:{ext_user_id}'
        result_list = TinkModelResultList(result=None, action=msg, msg='')

        # Get the required OAuth2 access code
        try:
            rl = self._oauth2_client_credentials_flow(grant_type='client_credentials',
                                                      client_scope='authorization:grant,user:read',
                                                      user_scope='user:read',
                                                      ext_user_id=ext_user_id)
            result_list.append(rl)
        except ex.UserNotExistingError as e:
            raise e

        msg = f'Get user ext_user_id:{ext_user_id}'
        service = api.UserService()
        response: api.UserResponse = service.get_user(ext_user_id=ext_user_id,
                                                      access_token=self._access_token)

        if response.http_status(cfg.HTTPStatusCode.Code2xx):
            result_status = TinkModelResultStatus.Success
            logging.info(msg + f' => ext_user_id:{ext_user_id} queried')
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        result_list.append(TinkModelResult(result_status, response, msg))

        return result_list

    def get_users(self):
        """
        "Get users from the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing instances of api.UserResponse with a unique identifier of
        the users {USER_ID}.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action=msg, msg='Get users')

        users = self._dao.users.data

        # Delete existing users
        key = 'userExternalId'
        for e in users:
            if isinstance(e, collections.OrderedDict):
                if key in e:
                    # Get user
                    msg = f'Get user {key}:{e[key]}...'
                    logging.info(msg)
                    try:
                        rl = self.get_user(ext_user_id=e[key])
                        result_list.append(rl)
                    except ex.UserNotExistingError as e:
                        result_list.append(e.result_list)

        # Store data in the DAO
        try:
            self._dao.tink_users = result_list.payload()
        except Exception as e:
            raise e

        # Write results into a file
        if cfg.TinkConfig.get_instance().result_file_flag:
            try:
                rl = self.save_data_to_file(entity_type=cfg.EntityType.User,
                                            fields=data.TinkDAO.fields_user_api_out,
                                            locator=cfg.TinkConfig.get_instance().user_target,
                                            payload=self._dao.tink_users.data)
                result_list.append(rl)
            except Exception as e:
                raise e

        return result_list

    def user_exists(self, ext_user_id):
        """
        Checks if a user does already exist in the Tink platform.
        :param ext_user_id: External user reference (this is NOT the Tink internal id).
        :return: Boolean - True if the user exists, otherwise False.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
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

    def ingest_accounts(self):
        """
        Initiates the ingestion of accounts per user into the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing instances of api.AccountIngestionResponse with a status code:
        STATUS CODE	DESCRIPTION
        204	Accounts created.
        400	The payload does not pass validation.
        401	User not found, has no credentials, or has more than one set of credentials.
        409	Account already exists.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action=msg, msg='Ingest accounts')

        # --- Authorize client
        rl = self._authorize_client(scope='authorization:grant,accounts:write')
        response: api.OAuth2AuthenticationTokenResponse = rl.last().response

        if rl.status() == TinkModelResultStatus.Success:
            client_access_token = response.access_token
        else:
            logging.error(response.summary())

        result_list.append(rl)

        # --- Ingest accounts per user
        users = self._dao.users.data
        service = api.AccountService(url_root=cfg.API_URL_TINK_CONNECTOR)

        for e in users:
            ext_user_id = e['userExternalId']
            msg = f'Ingest accounts for ext_user_id:{ext_user_id}'

            if not self._dao.accounts.contains_entities(ext_user_id):
                logging.info(msg + ' => Skipped (No accounts found)')
                continue

            response: api.AccountIngestionResponse = None
            user_accounts = self._dao.accounts.create_subset(ext_user_id=ext_user_id)
            response = service.ingest_accounts(ext_user_id=ext_user_id,
                                               accounts=user_accounts,
                                               client_access_token=client_access_token)

            if response.http_status(cfg.HTTPStatusCode.Code2xx):
                result_status = TinkModelResultStatus.Success
                logging.info(msg + ' => Done')
            else:
                logging.error(response.summary())
                result_status = TinkModelResultStatus.Error

            result_list.append(TinkModelResult(result_status, response, msg))

        return result_list

    def delete_accounts(self):
        """
        Initiates the deletion of accounts in the Tink platform.

        :return: TinkModelResult
        """
        pass

    def get_all_accounts(self):
        """
        "Get users from the Tink platform.

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing instances of api.UserResponse with a unique identifier of
        the users {USER_ID}.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(result=None, action=msg, msg='Get all accounts')

        users = self._dao.users.data

        key = 'userExternalId'
        for e in users:
            if isinstance(e, collections.OrderedDict):
                if key in e:
                    # Get user
                    msg = f'Get accounts of user {key}:{e[key]}...'
                    logging.info(msg)
                    try:
                        rl = self.get_user_accounts(ext_user_id=e[key])
                        result_list.append(rl)
                    except ex.UserNotExistingError as e:
                        result_list.append(e.result_list)

        # Store data in the DAO
        try:
            tink_accounts = data.TinkEntityList(entity_type=cfg.EntityType.Account)

            for r in result_list.get_elements(has_payload=True):
                entity_list = data.TinkEntityList.create_from_http_response(r.response)
                tink_accounts.append(entity_list)
            self._dao.tink_accounts = tink_accounts
        except Exception as e:
            raise e

        # Write results into a file
        if cfg.TinkConfig.get_instance().result_file_flag:
            try:
                rl = self.save_data_to_file(entity_type=cfg.EntityType.Account,
                                            fields=data.TinkDAO.fields_acc_api_out,
                                            locator=cfg.TinkConfig.get_instance().account_target,
                                            payload=self._dao.tink_accounts.data)
                result_list.append(rl)
            except Exception as e:
                raise e

        return result_list

    def get_user_accounts(self, ext_user_id=None):
        """
        Get list of all accounts of a user within the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)

        :return: TinkModelResultList wrapping TinkModelResult objects of all API calls performed
        containing an instance of api.AccountListResponse with a list of
        the user's accounts.
        :raise ExUserNotExisting: in case the user to be deleted does not exist
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.debug(msg)

        # Wrapper for the results
        msg = f'Get accounts of the user with ext_user_id:{ext_user_id}'
        result_list = TinkModelResultList(result=None, action=msg, msg='')

        # Get the required OAuth2 access code
        try:
            rl = self._oauth2_client_credentials_flow(grant_type='client_credentials',
                                                      client_scope='authorization:grant,accounts:read',
                                                      user_scope='accounts:read',
                                                      ext_user_id=ext_user_id)
            result_list.append(rl)
        except ex.UserNotExistingError as e:
            raise e

        msg = f'Get accounts for user ext_user_id:{ext_user_id}'
        service = api.AccountService(url_root=cfg.API_URL_TINK)
        response: api.AccountListResponse = service.list_accounts(ext_user_id=ext_user_id,
                                                                  access_token=self._access_token)

        if response.http_status(cfg.HTTPStatusCode.Code2xx):
            result_status = TinkModelResultStatus.Success
            logging.info(msg + f' => done')
        else:
            logging.error(response.summary())
            result_status = TinkModelResultStatus.Error

        result_list.append(TinkModelResult(result_status, response, msg))

        return result_list

    def ingest_transactions(self):
        """
        Initiates the ingestion of transactions in the Tink platform.

        :return: TinkModelResult
        """
        pass

    def delete_transactions(self):
        """
        Initiates the deletion of transactions in the Tink platform.

        :return: TinkModelResult
        """
        pass

    def list_transactions(self):
        """
        Initiates the retrieval of a list of all transactions in the Tink platform.

        :return: TinkModelResult
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # Wrapper for the results
        result_list = TinkModelResultList(msg='')

        return result_list

    def list_categories(self):
        """
        Get a list of all categories in the Tink platform.

        :return: TinkModelResultList
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
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
                 msg: str = '',
                 is_important: bool = False):
        """
        Initialization.

        :param status: Reference to an instance of the Enum class TinkResultStatus.
        :param response: Reference to an instance of a sub-class of the class api.TinkAPIResponse.
        :param action: A description of the action performed.
        :param msg: A message describing the main activity performed.
        :param is_important: Boolean saying to ideally not ignore this result's contents (e.g. in output)
        since it contains important information.
        """
        self._status = status
        self._response = response

        self._action = action
        if self._action == '':
            self._action = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'

        self._msg = msg
        self._is_important = is_important

    def get(self, key):
        """
        Get a value from the dictionary self.data in case of existence.

        :param key: key for the dictionary lookup
        :return: the value if there could one be found in the dictionary
        """
        if key in self._response.data:
            return self._response.data[key]
        else:
            return ''

    @property
    def status(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._status

    @status.setter
    def status(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._status = value

    @property
    def response(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._response

    @property
    def action(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._action

    @action.setter
    def action(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._action = value

    @property
    def msg(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._msg = value


    @property
    def is_important(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._is_important


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

        self._action = action
        if self._action == '':
            self._action = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'

        self._msg = msg

        # If provided save a list containing the initial result items
        if isinstance(result, TinkModelResult):
            self.results.append(result)
        else:
            logging.debug('Parameter "result" was ignored since it was not of expected type TinkModelResult')

    @property
    def action(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._action

    @action.setter
    def action(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._action = value

    @property
    def msg(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._msg

    @msg.setter
    def msg(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._msg = value

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

    def append(self, result):
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

    def get_elements(self,
                     endpoints: list = None,
                     has_payload: bool = None,
                     is_important: bool = None,
                     is_exception: bool = None):
        """
        Get the latest TinkModelResult object in the list result_items for which the
        given filters apply.
        Hint: The filters (parameters) are being interpreted as a logical AND meaning only
        if all of the conditions provided are fulfilled the item will be added to the result.

        :param endpoints: Do only return results whose response endpoints matches the given
        list of (sub)strings.
        :param is_important: Filter =>  Include results that have set the flag "is_important".
        :param has_payload: Filter => Include results that have set the flag "has_payload".
        :param is_exception: Filter => Include results that have TinkModelResultStatus.Exception.
        :return TinkModelResult: A list of TinkModelResult objects matching the filter criteria.
        """
        lst = list()
        for result in self.results:
            # Filter 1: Do only consider special endpoints
            if endpoints:
                for endpoint in endpoints:
                    if result.response.request.endpoint.find(endpoint) != -1:  # Found
                        lst.append(result)
            # Filter 2: Add responses that have any payload if requested
            if has_payload:
                if result.response.has_payload == has_payload:
                    lst.append(result)
            # Filter 3: Add responses that have a flag to not ignore these ideally
            if is_important:
                if result.is_important is is_important:
                    lst.append(result)
            # Exceptions should ALWAYS be shown!
            if is_exception:
                if result.status == TinkModelResultStatus.Exception:
                    lst.append(result)

        return lst

    def count(self, status: TinkModelResultStatus):
        """
        Count all elements having the given status.

        :param status: Reference to an instance of the Enum class TinkResultStatus.
        :return: The number of elements in the list self.result with the requested status.
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
                text += sep + f'{cnt}/{len(self.results)} steps: {str(s.value)}'

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
                if k == 'endpoints':
                    endpoints = filters[k]
        else:
            endpoints = None

        # Overall status over all results wrapped within this result list
        text = f'{self._action} ... {self.status().value} [{self._msg}]'

        # Overall statistics

        level = cfg.TinkConfig.get_instance().message_detail_level

        if level == cfg.MessageDetailLevel.High:
            text += os.linesep + self.statistics()
        else:
            logging.debug(self.statistics())

        # Reduce amount of results by using the provided filters
        if level == cfg.MessageDetailLevel.Low:
            # Print certain results only (of the list of actions performed)
            rl: list[TinkModelResult] = self.get_elements(endpoints=endpoints,
                                                          is_important=True,
                                                          is_exception=True)
        else:
            rl = self.results

        # Summarize the status of the single steps
        if level == cfg.MessageDetailLevel.Low:
            for r in rl:
                text += os.linesep + f'{r.action} ... {r.status.value}'
                if r.msg and r.msg != r.status.value:
                    text += f' [{r.msg}]'
                if r.response:
                    text += f' [{r.response.summary()}]'
        elif level == cfg.MessageDetailLevel.Medium:
            for i in range(len(self.results)):
                text += f'\nResult #{i+1}\n{self.results[i].response.summary()}'

        return text

    def payload(self, entity_type: cfg.EntityType = None):
        """
        Get the payload (data) out of all contained result items.
        The main purpose of this method is to provide an easy to use interface in order
        to retrieve the data received from an API endpoint in order to further process
        the data.
        :param entity_type: The entity type of interest.
        :return: The relevant payload over all responses wrapped into the result list
        elements contained.
        """
        result_data = list()
        for result in self.results:
            if result.response.has_payload:

                payload = result.response.payload
                # TODO: Adjust definition of payload
                #  1. Only consider responses that have has_payload = True
                #  2. If payload is a list then append the items of the
                #  list rather than the list itself
                #  Or do the job using a new TinkEntityList.create_from_http_response
                result_data.append(payload)

        return result_data


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
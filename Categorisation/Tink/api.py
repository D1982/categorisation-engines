"""Direct access to Tink's API endpoints. """
from json import JSONDecodeError

import Categorisation.Common.config as cfg
import Categorisation.Common.util as utl
import Categorisation.Common.secret as secret
import Categorisation.Tink.api as api
import Categorisation.Tink.data as data


import os
import sys
import collections
import logging
import requests
import json

import abc  # https://pymotw.com/3/abc/


class TinkAPI:

    """
    Base class for all service wrapper classes accessing Tink API services.
    """

    def __init__(self, url_root=cfg.API_URL_TINK):
        """
        Initialization.

        :param url_root: URL root string of the API
        """
        self.url_root: str = url_root
        self.partner_info: dict = dict()
        self.partner_info['client_id'] = secret.TINK_CLIENT_ID
        self.partner_info['client_secret'] = secret.TINK_CLIENT_SECRET


class TinkAPIRequest(metaclass=abc.ABCMeta):

    """
    Wrapper class for a request to the Tink API.
    """

    def __init__(self, method: str, endpoint: str):
        """
        Initialization.

        :param method: http method GET, POST, PUT, ...
        :param endpoint: the correct http endpoint to be concatenated with the url root string
        """
        self.method: str = method
        self.endpoint: str = endpoint
        self.headers: collections.OrderedDict = collections.OrderedDict()
        self.data: collections.OrderedDict = collections.OrderedDict()

    def to_string(self):
        text = 'HTTP Request: {m} {t}'.format(m=self.method, t=self.endpoint)

        return str(text)

    def to_string_formatted(self):
        text = self.to_string() + os.linesep

        for k, v in self.headers.items():
            text += 'Header > ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + os.linesep

        for k, v in self.data.items():
            text += 'Body > ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + os.linesep

        return str(text)


class TinkAPIResponse(metaclass=abc.ABCMeta):

    """
    Abstract wrapper class for a response object of the Python requests library.

    The intention of this class is to enrich the response object f the requests library
    with additional information and functionality like e.g. the method to_string_formatted()
    """

    def __init__(self, request: api.TinkAPIRequest, response: requests.Response = None):
        """
        Initialization.

        :param request: corresponding TinkAPIRequest for that TinkAPIResponse
        :param response: an instance of the class requests.Response
        """
        # Data to be populated by sub-classes
        self.names: tuple
        self.data: collections.OrderedDict = collections.OrderedDict()
        self.json: dict = dict()

        self.status_code: int = -1
        self.reason: str = ''
        self.content: bytes = b''
        self.text: str = ''

        # Response JSON
        try:
            if response:
                self.json = response.json() or dict()
        except Exception as e:
            logging.warning("Exception in Function call requests.response.json() -> {e}".format(e=e))
            # This service does not return a JSON so just use the text instead
            self.json = {'text': response.text}

        # Response Attributes
        if isinstance(response, requests.Response):
            self.status_code = response.status_code
            self.reason = response.reason
            self.content = response.content
            self.text = response.text

        # Store the corresponding TinkAPIRequest and the requests.Response
        self.request: api.TinkAPIRequest = request
        self.response_orig: requests.Response = response

    def to_string(self):
        """
        Minimalistic string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        if self.response_orig is not None:
            code = self.response_orig.status_code
            reason = self.response_orig.reason
            text = 'HTTP Response: {c} ({r})'.format(c=code, r=reason)
        else:
            text = os.linesep + 'HTTP Response: Unbound'

        return str(text)

    def to_string_formatted(self):
        """
        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        text = self.to_string() + os.linesep

        if self.json and isinstance(self.json, dict):
            for k, v in self.json.items():
                text += 'JSON > ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + os.linesep

        if self.json and isinstance(self.json, list):
            for e in self.json:
                if isinstance(e, dict):
                    for k, v in e.items():
                        text += str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + ', '
                    text += os.linesep
        if self.data:
            for k, v in self.data.items():
                if k not in self.json:
                    text += 'Data > ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        return str(text)

    @abc.abstractmethod
    def to_string_custom(self):  # Abstract method to be overridden in sub-classes
        """
        Custom string representation of a TinkAPIResponse instance.

        This is an abstract method to provide a formatted string representation of the data
        within an instance of this class.

        Hint: This is an abstract method that can be overridden in a sub-class that requires a
        special way of formatting. See as an example the class api.CategoryService which has
        it'S own method in order to print a list of categories.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # TODO: Raise exception NotImplementedError
        # This exception is derived from RuntimeError.
        # In user defined base classes, abstract methods should raise this exception
        # when they require derived classes to override the method, or while the class
        # is being developed to indicate that the real implementation still needs to be added.
        return ''

    def http_status(self, group: cfg.HTTPStatusCode = None):
        """
        Checks whether a http status code is >= 200 and < 300.

        :param group: http status code group according to cfg.HTTPStatusCode
        :return: True if the http status code of this request belongs
        to group, otherwise False
        """
        if not group:
            return False
        # 2xx
        if group == cfg.HTTPStatusCode.Code2xx:
            if self.status_code in range(200, 299):
                return True
            else:
                return False
        # 4xx
        if group == cfg.HTTPStatusCode.Code4xx:
            if self.status_code in range(400, 499):
                return True
            else:
                return False
        # 5xx
        if group == cfg.HTTPStatusCode.Code5xx:
            if self.status_code in range(500, 599):
                return True
            else:
                return False

    def summary(self):
        """
        Print a summary of the response and the corresponding request.

        :return: Text as a string
        """
        summary_text = ''
        payload_text = ''

        level = utl.message_detail_level()

        try:
            payload = json.loads(self.text)
            payload_text = payload
        except JSONDecodeError as e:
            logging.warning(str(e))
            payload = dict()
            payload_text = ''

        # Payload for errors (4xx status code)
        if self.http_status(cfg.HTTPStatusCode.Code4xx):
            if 'errorMessage' in payload:
                payload_text = payload['errorMessage']
            elif 'errorCode' in payload:
                payload_text = payload['errorCode']
        # Payload per specific successful responses (2xx status code)
        elif self.http_status(cfg.HTTPStatusCode.Code2xx):
            if self.request.endpoint.find('/api/v1/monitoring/') != -1:
                payload_text = self.text
            if self.request.endpoint.find('/user/create') != -1:
                if 'user_id' in payload:
                    payload_text = 'user_id:{u}'.format(u=payload['user_id'])
        else:
            payload_text = ''

        if level == cfg.MessageDetailLevel.Low:
            summary_text = '{s}: {p}'.format(s=self.to_string(),
                                             p=payload_text)
        elif level == cfg.MessageDetailLevel.Medium:
            summary_text = '{s} {p}: {c}'.format(s=self.to_string(),
                                                 p=payload_text,
                                                 c=self.content)
        elif level == cfg.MessageDetailLevel.High:
            summary_text = '{s} {req}: {resp}'.format(s=self.to_string(),
                                                      req=self.request.to_string_formatted(),
                                                      resp=self.to_string_formatted())
        return summary_text


class MonitoringService(TinkAPI):

    """
    Wrapper class for the Tink monitoring service.
    """

    def __init__(self):
        """
        Initialization.
        """
        super().__init__()

    def ping(self):
        """
        Call the API endpoint /api/v1/monitoring/ping

        :return: A response wrapper object (instance of api.MonitoringResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='GET', endpoint=self.url_root+'/api/v1/monitoring/ping')
        response = requests.get(url=request.endpoint)

        return MonitoringResponse(request, response)

    def health_check(self):
        """
        Call the API endpoint /api/v1/monitoring/healthy

        :return: A response wrapper object (instance of api.TinkAPIResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='GET', endpoint=self.url_root+'/api/v1/monitoring/healthy')
        response = requests.get(url=request.endpoint)

        return MonitoringResponse(request, response)


@TinkAPIResponse.register
class DummyResponse(TinkAPIResponse):

    """
    Wrapper class for an empty or not existing response.

    An example would be that an action do delete a user was stopped
    before an appropriate API request was sent because a previous check
    found out that the user did not exist.
    """

    def __init__(self, ):
        """
        Initialization.
        """
        request = TinkAPIRequest(method='DummyMethod', endpoint='DummyEndpoint')
        super().__init__(request, None)

        # Define fields of interest referring to the official API documentation
        self.names = {'errorMessage', 'errorCode'}

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()


@TinkAPIResponse.register
class MonitoringResponse(TinkAPIResponse):

    """
    Wrapper class for the Tink monitoring service response.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Define fields of interest referring to the official API documentation
        self.names = {'errorMessage', 'errorCode'}

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()


class CategoryService(TinkAPI):

    """
    Wrapper class for the Tink category service.
    """

    def __init__(self):
        """
        Initialization.
        """
        super().__init__()

    def list_categories(self):
        """
        Call the API endpoint /api/v1/categories

        :return: A response wrapper object (instance of api.CategoryResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='GET', endpoint=self.url_root+'/api/v1/categories')
        response = requests.get(url=request.endpoint)

        return CategoryResponse(request, response)


@TinkAPIResponse.register
class CategoryResponse(TinkAPIResponse):

    """
    Wrapper class for a Tink category service response.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Define fields of interest referring to the official API documentation
        self.names = {'primaryName', 'secondaryName', 'typeName', 'code', 'type', 'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}

    def to_string_custom(self):
        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        text = self.to_string() + os.linesep

        if self.json and isinstance(self.json, list):
            for e in self.json:
                if isinstance(e, dict):
                    for k, v in e.items():
                        if k in self.names:
                            text += str(k) + ':' + str(v)[0:cfg.UI_STRING_MAX_WITH] + ', '
                    text += os.linesep
        else:
            text += self.to_string_formatted()

        return str(text)


class UserService(TinkAPI):

    """
    Wrapper class for the Tink user service.
    """

    def __init__(self):
        """
        Initialization.
        """
        super().__init__()

    def activate_user(self, ext_user_id, label, market, locale, client_access_token):
        """
        Call the API endpoint /api/v1/user/create

        Create a new user in the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param label: description of the user like e.g. the name
        :param market: ISO country code like e.g. UK, DE, CH
        :param locale: ISO language code like e.g. en_US, en_GB, de_CH, fr_CH
        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)
        :return: A response wrapper object (instance of api.UserActivationResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root+'/api/v1/user/create')
        # --- Header
        request.headers.update({'Authorization': 'Bearer ' + client_access_token})
        request.headers.update({'Content-Type': 'application/json'})
        # --- Body
        request.data.update({'market': market})
        request.data.update({'locale': locale})
        request.data.update({'label': label})
        request.data.update({'external_user_id': ext_user_id})

        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(b=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=json.dumps(request.data), headers=request.headers)

        return UserActivationResponse(request, response)

    def delete_user(self, access_token):
        """
        Call the API endpoint /api/v1/user/delete

        Delete an existing user in the Tink platform.

        The client_access_token must have been gathered from a call like
        authorize_client_delete(..., scope='user:delete', delete_dict) whereas
        delete_dict should have contained the user_id or ext_user_id of the
        user that should be deleted.

        Otherwise this call will fail with code 401 Unauthorized

        :param access_token: The OAuth2 user access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.grant_user_access(...)
        :return: A response wrapper object (instance of api.UserDeleteResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root + '/api/v1/user/delete')
        # --- Header
        request.headers.update({'X-Tink-OAuth-Client-ID': secret.TINK_CLIENT_ID})
        request.headers.update({'Authorization': 'Bearer {t}'.format(t=access_token)})
        request.headers.update({'Content-Type': 'application/json'})
        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(b=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=json.dumps(request.data), headers=request.headers)

        return UserDeleteResponse(request, response)


@TinkAPIResponse.register
class UserActivationResponse(TinkAPIResponse):

    """
    Abstract wrapper class for UserActivationResponse from Tink's user service.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Custom attributes relevant for this response
        self.user_id = None

        # Define fields of interest referring to the official API documentation
        self.names = {'user_id', 'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'user_id' in self.data:
                    self.user_id = self.data['user_id']

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()


class UserDeleteResponse(TinkAPIResponse):

    """
    Abstract wrapper class for UserDeleteResponse from Tink's user service.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Custom attributes relevant for this response
        self.user_id = None

        # Define fields of interest referring to the official API documentation
        self.names = {'user_id', 'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 204:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'user_id' in self.data:
                    self.user_id = self.data['user_id']

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()


class AccoungService(TinkAPI):

    """
    Wrapper class for the Tink account service.
    """

    def __init__(self, url_root=cfg.API_URL_TINK_CONNECTOR):
        """
        Initialization.
        """
        super().__init__(url_root)

    def ingest_accounts(self, ext_user_id, accounts: data.TinkAccountList, client_access_token):
        """
        Call the Connector API endpoint users/{{external-user-id}}/accounts

        Ingest a list of accunts into the space of an existing user in the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param accounts: A dictionary containing the account data to be ingested
        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)

        :return: a response wrapper object (instance of api.AccountIngestionResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # --- Request
        endpoint = self.url_root+'/users/{u}/accounts'.format(u=ext_user_id)
        request = TinkAPIRequest(method='POST', endpoint=endpoint)
        # --- Header
        request.headers.update({'Authorization': 'Bearer ' + client_access_token})
        request.headers.update({'Content-Type': 'application/json'})
        # --- Body
        user_accounts = accounts.get_data(ext_user_id=ext_user_id)
        request.data.update({'accounts': user_accounts})
        json_data = json.dumps(request.data)
        # --- Logging
        logging.debug(f'{request.method} {request.endpoint}')
        logging.debug(f'Request Header: {request.headers}')
        logging.debug(f'Request Body: {json_data}')
        # --- API call
        response = requests.post(url=request.endpoint,
                                 data=json_data,
                                 headers=request.headers)

        return AccountIngestionResponse(request, response)

@TinkAPIResponse.register
class AccountIngestionResponse(TinkAPIResponse):

    """
    Abstract wrapper class for AccountIngestionResponse from Tink's account service.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Custom attributes relevant for this response

        # Define fields of interest referring to the official API documentation
        self.names = {'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'user_id' in self.data:
                    self.user_id = self.data['user_id']

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()


class AccountListResponse(TinkAPIResponse):

    """
    Abstract wrapper class for AccountListResponse from Tink's user service.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Custom attributes relevant for this response
        self.user_id = None

        # Define fields of interest referring to the official API documentation
        self.names = {'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 204:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'user_id' in self.data:
                    self.user_id = self.data['user_id']

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()


class OAuthService(TinkAPI):

    """
    Wrapper class for the Tink OAuth service.
    """

    def __init__(self):
        """
        Initialization.
        """
        super().__init__()

    def authorize_client_access(self, grant_type, scope, delete_dict=None):
        """
        Call the API endpoint /api/v1/oauth/token

        Authorize access to the client (company account).

        This method will gather an access token (valid only for the authenticated client)
        that can be used to manipulate the users tied to TINK_CLIENT_ID.
        The access token usually expires after 30 mins and can be renewed with an
        appropriate refresh token that should also be kept as a secret (like the client secret)

        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials
        :param scope: the requested scope when using client credentials.
        :param delete_dict: If delete_dict is provided then the service has to be used to delete data.
        This is a workaround that can be used in order to delete existing users and accounts

        :return: OAuth2AuthenticationTokenResponse
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root + '/api/v1/oauth/token')
        # --- Body
        request.data.update({'scope': scope})
        if delete_dict:  # TODO: Add accounts in case of deletion for accounts is also working
            if 'ext_user_id' in delete_dict:
                request.data.update({'ext_user_id': delete_dict['ext_user_id']})
            elif 'user_id' in delete_dict:
                request.data.update({'user_id': delete_dict['user_id']})
        request.data.update({'client_id': secret.TINK_CLIENT_ID})
        request.data.update({'client_secret': secret.TINK_CLIENT_SECRET})
        request.data.update({'grant_type': grant_type})

        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(b=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=request.data)

        return OAuth2AuthenticationTokenResponse(request, response)

    def grant_user_access(self, client_access_token, user_id=None, ext_user_id=None, scope='user:read'):
        """
        Grant an access code to perform an action that was previously authorized.

        Call the API endpoint /api/v1/oauth/authorization-grant
        https://docs.tink.com/enterprise/api/#create-an-authorization-for-the-given-user-id-with-requested-scopes

        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)
        :param user_id: the unique Tink user identifier
        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param scope: the requested scope when using client credentials.

        :return: TinkModelResult containing an instance of api.OAuth2AuthorizeResponse with an
        authorization code {CODE}.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root + '/api/v1/oauth/authorization-grant')
        # --- Headers
        request.headers.update({'Authorization': 'Bearer {t}'.format(t=client_access_token)})
        # --- Body
        request.data.update({'scope': scope})
        if user_id:
            request.data.update({'user_id': user_id})
        elif ext_user_id:
            request.data.update({'external_user_id': ext_user_id})
        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(b=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=request.data, headers=request.headers)

        return OAuth2AuthorizeResponse(request, response)

    def get_oauth_access_token(self, code, grant_type='authorization_code'):
        """
        Get the OAuth access token for the user to perform an action that was previously authorized.

        Wrapper for the API endpoint /api/v1/oauth/token
        ​https://api.tink.se/api/v1/oauth/token

        :param code: the authorization code gathered via the endpoint /api/v1/oauth/token which can
        be called using OAuthService.grant_user_access(...)
        :param grant_type: the grant type. values: authorization_code, refresh_token, client_credentials

        :return: TinkModelResult containing an instance of api.OAuth2AuthenticationTokenResponse with a
        client access token {ACCESS_TOKEN}.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root + '/api/v1/oauth/token')
        # --- Body
        request.data.update({'code': code})
        request.data.update({'client_id': secret.TINK_CLIENT_ID})
        request.data.update({'client_secret': secret.TINK_CLIENT_SECRET})
        request.data.update({'grant_type': grant_type})
        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(b=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=request.data)

        return OAuth2AuthenticationTokenResponse(request, response)


@TinkAPIResponse.register
class OAuth2AuthenticationTokenResponse(TinkAPIResponse):

    """
    Abstract wrapper class for a AuthenticationResponse from Tink's OAuth service.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Custom attributes relevant for this response
        self.access_token = None
        self.token_type = None
        self.expires_in = None
        self.scope = None
        self.id_hint = None

        # Define fields of interest referring to the official API documentation
        self.names = {'access_token', 'token_type', 'expires_in', 'scope', 'id_hint', 'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'access_token' in self.data:
                    self.access_token = self.data['access_token']
                if 'token_type' in self.data:
                    self.token_type = self.data['token_type']
                if 'expires_in' in self.data:
                    self.expires_in = self.data['expires_in']
                if 'scope' in self.data:
                    self.scope = self.data['scope']
                if 'id_hint' in self.data:
                    self.id_hint = self.data['id_hint']

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()


@TinkAPIResponse.register
class OAuth2AuthorizeResponse(TinkAPIResponse):

    """
    Abstract wrapper class for a AuthorizeResponse from Tink's OAuth service.
    """

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Custom attributes relevant for this response
        self.code = None

        # Define fields of interest referring to the official API documentation
        self.names = {'code', 'errorMessage', 'errorCode'}

        # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
        self.data = {key: value for key, value in self.json.items() if key in self.names}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'code' in self.data:
                    self.code = self.data['code']

    def to_string_custom(self):

        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        # No override required - use standard output
        return self.to_string_formatted()

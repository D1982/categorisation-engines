"""Direct access to Tink's API endpoints. """

import Categorisation.Common.config as cfg
import Categorisation.Common.secret as secret
import Categorisation.Tink.api as api

import os
import sys
import collections
import logging
import requests
import json

import abc  # https://pymotw.com/3/abc/


"""Base class for all service wrapper classes accessing Tink API services."""


class TinkAPI:

    def __init__(self, url_root=cfg.API_URL_TINK):
        """
        Initialization.

        :param url_root: URL root string of the API
        """
        self.url_root: str = url_root

        self.partner_info: dict = dict()
        self.partner_info['client_id'] = secret.TINK_CLIENT_ID
        self.partner_info['client_secret'] = secret.TINK_CLIENT_SECRET


"""Wrapper class for a request to the Tink API."""


class TinkAPIRequest(metaclass=abc.ABCMeta):

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
        self.status_code: str = '0'
        self.reason: str = 'Dummy'

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


"""Abstract wrapper class for a response object of the Python requests library.

The intention of this class is to enrich the response object f the requests library
with additional information and functionality like e.g. the method to_string_formatted()
"""


class TinkAPIResponse(metaclass=abc.ABCMeta):

    def __init__(self, request: api.TinkAPIRequest, response: requests.Response):
        """
        Initialization.

        :param request: corresponding TinkAPIRequest for that TinkAPIResponse
        :param response: an instance of the class requests.Response
        """
        # Store the corresponding TinkAPIRequest for that TinkAPIResponse
        self.request: api.TinkAPIRequest = request
        self.response_orig: requests.Response = response

        # Data to be populated by sub-classes
        self.names: tuple
        self.data: collections.OrderedDict = collections.OrderedDict()
        self.json: dict = dict()

        # Response JSON
        try:
            if self.response_orig:
                self.json = response.json() or dict()
        except Exception as e:
            logging.warning("Exception in Function call requests.response.json() -> {e}".format(e=e))
            # This service does not return a JSON so just use the text instead
            self.json = {'text': response.text}

    """"""
    def to_string(self):
        """
        Minimalistic string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        if self.response_orig:
            text = 'HTTP Response: ' + self.response_orig.reason + ' ({code})'.format(
                                                code=str(self.response_orig.status_code))
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
                    text += 'Data > ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + os.linesep

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
        return ''


"""Wrapper class for the Tink monitoring service."""


class MonitoringService(TinkAPI):

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
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        request = TinkAPIRequest(method='GET', endpoint=self.url_root+'/api/v1/monitoring/ping')
        response = requests.get(url=request.endpoint)

        return MonitoringResponse(request, response)

    def health_check(self):
        """
        Call the API endpoint /api/v1/monitoring/healthy

        :return: A response wrapper object (instance of api.TinkAPIResponse)
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        request = TinkAPIRequest(method='GET', endpoint=self.url_root+'/api/v1/monitoring/healthy')
        response = requests.get(url=request.endpoint)

        return MonitoringResponse(request, response)


"""Wrapper class for the Tink monitoring service response."""


@TinkAPIResponse.register
class MonitoringResponse(TinkAPIResponse):

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


"""Wrapper class for the Tink category service."""


class CategoryService(TinkAPI):

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
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        request = TinkAPIRequest(method='GET', endpoint=self.url_root+'/api/v1/categories')
        response = requests.get(url=request.endpoint)

        return CategoryResponse(request, response)


"""Wrapper class for a Tink category service response."""


@TinkAPIResponse.register
class CategoryResponse(TinkAPIResponse):

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Define fields of interest referring to the official API documentation
        self.names = {'primaryName', 'secondaryName', 'typeName', 'code', 'type', 'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if response and response.status_code == 200:
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


"""Wrapper class for the Tink user service."""


class UserService(TinkAPI):

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
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root+'/api/v1/user/create')
        # --- Header
        request.headers.update({'Authorization': 'Bearer ' + client_access_token})
        request.headers.update({'Content-Type': 'application/json'})
        # --- Body
        request.data.update({'external_user_id': ext_user_id})
        request.data.update({'label': label})
        request.data.update({'market': market})
        request.data.update({'locale': locale})
        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(h=request.data))
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
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root + '/api/v1/user/delete')
        # --- Header
        request.headers.update({'X-Tink-OAuth-Client-ID': secret.TINK_CLIENT_ID})
        request.headers.update({'Authorization': 'Bearer ' + access_token})
        request.headers.update({'Content-Type': 'application/json'})
        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(h=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=json.dumps(request.data), headers=request.headers)

        return UserDeleteResponse(request, response)


"""Abstract wrapper class for UserActivationResponse from Tink's user service."""


@TinkAPIResponse.register
class UserActivationResponse(TinkAPIResponse):

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
        if response and response.status_code == 204:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'user_id' in self.data.items():
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


"""Abstract wrapper class for UserDeleteResponse from Tink's user service."""


class UserDeleteResponse(TinkAPIResponse):

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
        if response and response.status_code == 204:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'user_id' in self.data.items():
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


"""Wrapper class for the Tink OAuth service."""


class OAuthService(TinkAPI):

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
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root + '/api/v1/oauth/token')
        # --- Body
        request.data.update({'client_id': secret.TINK_CLIENT_ID})
        request.data.update({'client_secret': secret.TINK_CLIENT_SECRET})
        request.data.update({'grant_type': grant_type})
        request.data.update({'scope': scope})
        if delete_dict:  # TODO: Add accounts in case of deletion for accounts is also working
            if 'external_user_id' in delete_dict:
                request.data.update({'ext_user_id': delete_dict['external_user_id']})
            elif 'user_id' in delete_dict:
                request.data.update({'user_id': delete_dict['user_id']})
        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(b=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=json.dumps(request.data), headers=request.headers)

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
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
        # --- Request
        request = TinkAPIRequest(method='POST', endpoint=self.url_root + '/api/v1/oauth/authorization-grant')
        # --- Headers
        request.headers.update({'Authorization: Bearer': client_access_token})
        # --- Body
        request.data.update({'scope': scope})
        if user_id:
            request.data.update({'user_id': user_id})
        else:
            request.data.update({'ext_user_id': ext_user_id})
        # --- Logging
        logging.debug('{m} {d}'.format(m=request.method, d=request.endpoint))
        logging.debug('Request Header: {h}'.format(h=request.headers))
        logging.debug('Request Body: {b}'.format(h=request.data))
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
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))
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
        logging.debug('Request Body: {b}'.format(h=request.data))
        # --- API call
        response = requests.post(url=request.endpoint, data=request.data)

        return OAuth2AuthenticationTokenResponse(request, response)


"""Abstract wrapper class for a AuthenticationResponse from Tink's OAuth service."""


@TinkAPIResponse.register
class OAuth2AuthenticationTokenResponse(TinkAPIResponse):

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
        self.names = {'access_token', 'token_type', 'expires_in', 'scope', 'id_hint' 'errorMessage', 'errorCode'}

        # Save fields of interest referring to the official API documentation
        if response and response.status_code == 200:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'access_token' in self.data.items():
                    self.access_token = self.data['access_token']
                if 'token_type' in self.data.items():
                    self.token_type = self.data['token_type']
                if 'expires_in' in self.data.items():
                    self.expires_in = self.data['expires_in']
                if 'scope' in self.data.items():
                    self.scope = self.data['scope']
                if 'id_hint' in self.data.items():
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


"""Abstract wrapper class for a AuthorizeResponse from Tink's OAuth service."""

@TinkAPIResponse.register
class OAuth2AuthorizeResponse(TinkAPIResponse):

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
        if response and response.status_code == 200:
            if isinstance(self.json, dict):
                self.data = {key: value for key, value in self.json.items() if key in self.names}
                if 'code' in self.data.items():
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

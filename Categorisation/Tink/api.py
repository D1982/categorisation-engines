"""Direct access to Tink's API endpoints. """
from json import JSONDecodeError

import Categorisation.Common.config as cfg
import Categorisation.Common.util as utl
import Categorisation.Common.secret as secret

import Categorisation.Tink.api as api
import Categorisation.Tink.data as data

from datetime import datetime


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
        :param level of detail currently chosen for ui logs

        """
        self._url_root: str = url_root
        self.partner_info: dict = dict()
        self.partner_info['client_id'] = secret.TINK_CLIENT_ID
        self.partner_info['client_secret'] = secret.TINK_CLIENT_SECRET

    @property
    def url_root(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._url_root

    @url_root.setter
    def url_root(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._url_root = value


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
        self._method: str = method
        self._endpoint: str = endpoint
        self._headers: dict = dict()
        self._payload: dict = dict()
        self._ext_user_id: str = ''  # To be set via property ext_user_id

    @property
    def method(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._method

    @property
    def endpoint(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._endpoint

    @property
    def headers(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._headers

    @headers.setter
    def headers(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._headers = value

    @property
    def payload(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._payload

    @payload.setter
    def payload(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._payload = value

    @property
    def ext_user_id(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._ext_user_id

    @ext_user_id.setter
    def ext_user_id(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._ext_user_id = value

    def log(self):
        logging.debug(f'{self._method} {self._endpoint}')
        logging.debug(f'Request Header: {self._headers}')
        logging.debug(f'Request Body: {self._payload}')

    def to_string(self):
        text = f'HTTP Request: {self._method} {self._endpoint}'

        return str(text)

    def to_string_formatted(self):
        text = self.to_string() + os.linesep

        for k, v in self._headers.items():
            text += 'Header > ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + os.linesep

        for k, v in self._payload.items():
            text += 'Body > ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + os.linesep

        return str(text)


class TinkAPIResponse(metaclass=abc.ABCMeta):

    """
    Abstract wrapper class for a response object of the Python requests library.

    The intention of this class is to enrich the response object f the requests library
    with additional information and functionality like e.g. the method to_string_formatted()
    """

    # Define fields/payload of interest referring to the official API documentation
    fieldnames: tuple = ('errorMessage', 'errorCode')

    def __init__(self, request: api.TinkAPIRequest, response: requests.Response = None):
        """
        Initialization.

        :param request: corresponding TinkAPIRequest for that TinkAPIResponse
        :param response: an instance of the class requests.Response

        :raise AttributeError: If one of the parameters is not of the expected type.
        """

        if not isinstance(request, TinkAPIRequest):
            msg = f'Expected type of parameter "request" is {type(api.TinkAPIRequest)} not {type(request)}'
            raise AttributeError(msg)

        # Data to be populated by sub-classes
        self._payload = dict()
        self._json = dict()

        self._status_code: int = -1
        self._reason: str = ''
        self._content: bytes = b''
        self._text: str = ''

        self._has_payload: bool = False
        self._fields: tuple = __class__.fieldnames
        self._entity_type: cfg.EntityType = cfg.EntityType.NotApplicable

        # Response JSON
        try:
            if response:
                self._json = response.json() or dict()
        except Exception as e:
            logging.warning(f'Exception in call requests.response.json() -> {e}')
            # This service does not return a JSON so just use the text instead
            self._json = {'text': response.text}

        # Response Attributes
        if isinstance(response, requests.Response):
            self._status_code = response.status_code
            self._reason = response.reason
            self._content = response.content
            self._text = response.text

        # Store the corresponding TinkAPIRequest and the requests.Response
        self.request: api.TinkAPIRequest = request
        self.response_orig: requests.Response = response

    @property
    def status_code(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._status_code

    @property
    def fields(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._fields

    @property
    def has_payload(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._has_payload

    @has_payload.setter
    def has_payload(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._has_payload = value


    @property
    def payload(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._payload

    def to_string(self):
        """
        Minimalistic string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        if self.response_orig is not None:
            code = self.response_orig.status_code
            reason = self.response_orig.reason
            text = f'HTTP Response: {code} ({reason})'
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

        try:
            self.to_string_custom()
        except NotImplementedError:
            # If there is no custom implementation available use the standard formatting
            if self._json and isinstance(self._json, dict):
                for k, v in self._json.items():
                    text += 'JSON -> ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + os.linesep

            if self._json and isinstance(self._json, list):
                for e in self._json:
                    if isinstance(e, dict):
                        for k, v in e.items():
                            text += str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH] + ', '
                        text += os.linesep
            if self._payload:
                for k, v in self._payload.items():
                    if k not in self._json:
                        text += 'DATA -> ' + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

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
        raise NotImplementedError

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
            if self._status_code in range(200, 299):
                return True
            else:
                return False
        # 4xx
        if group == cfg.HTTPStatusCode.Code4xx:
            if self._status_code in range(400, 499):
                return True
            else:
                return False
        # 5xx
        if group == cfg.HTTPStatusCode.Code5xx:
            if self._status_code in range(500, 599):
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

        try:
            payload = json.loads(self._text)
            payload_text = str(payload)
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
            # https://api.tink.se/api/v1/monitoring
            if self.request._endpoint.find('https://api.tink.se/api/v1/monitoring/') != -1:
                payload_text = self._text
            # https://api.tink.se/api/v1/user/delete
            elif self.request._endpoint.find('https://api.tink.se/api/v1/user/delete') != -1:
                pass
            # https://api.tink.se/api/v1/user/create
            elif self.request._endpoint.find('https://api.tink.se/user/create') != -1:
                if 'user_id' in payload:
                    payload_text = f'user_id:{payload["user_id"]}'
            # https://api.tink.se/api/v1/user/
            elif self.request._endpoint.find('https://api.tink.se/api/v1/user') != -1:
                if 'created' in payload and 'id' in payload:
                    created = payload['created']
                    d = utl.strdate(datetime.fromtimestamp(created/1000))
                    user_id = payload['id']
                    payload_text = f'created:{d}, user_id:{user_id}'
            # https://api.tink.se/api/v1/accounts/list
            elif self.request._endpoint.find('https://api.tink.se/api/v1/accounts/list') != -1:
                if isinstance(self._json, dict):
                    if 'accounts' in self._json:
                        cnt = len(self._json['accounts'])
                        payload_text = f'{cnt} items received'
            # https://api.tink.com/connector/users/{{ext-user-id}}/accounts
            elif self.request._endpoint.find('/accounts') != -1:
                if isinstance(self.request._payload, dict):
                    if 'accounts' in self.request._payload:
                        cnt = len(self.request._payload['accounts'])
                        payload_text = f'{cnt} items ingested'
            else:
                payload_text = ''

        level = cfg.TinkConfig.get_instance().message_detail_level

        if level == cfg.MessageDetailLevel.Low:
            summary_text = f'{self.to_string()}: {payload_text}'
        elif level == cfg.MessageDetailLevel.Medium:
            summary_text = f'{self.to_string()} {payload_text}: {self._content}'
        elif level == cfg.MessageDetailLevel.High:
            summary_text = f'{self.to_string()} ' \
                           f'{self.request.to_string_formatted()}: ' \
                           f'{self.to_string_formatted()}'\

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

        request = TinkAPIRequest(method='GET', endpoint=self._url_root + '/api/v1/monitoring/ping')
        response = requests.get(url=request.endpoint)

        return MonitoringResponse(request, response)

    def health_check(self):
        """
        Call the API endpoint /api/v1/monitoring/healthy

        :return: A response wrapper object (instance of api.TinkAPIResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='GET', endpoint=self._url_root + '/api/v1/monitoring/healthy')
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

    fieldnames: tuple = TinkAPIResponse.fieldnames

    def __init__(self, ):
        """
        Initialization.
        """
        request = TinkAPIRequest(method='DummyMethod', endpoint='DummyEndpoint')
        super().__init__(request, None)

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

    fieldnames: tuple = TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

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

        request = TinkAPIRequest(method='GET', endpoint=self._url_root + '/api/v1/categories')
        response = requests.get(url=request.endpoint)

        return CategoryResponse(request, response)


@TinkAPIResponse.register
class CategoryResponse(TinkAPIResponse):

    """
    Wrapper class for a Tink category service response.
    """

    fieldnames: tuple = ('primaryName', 'secondaryName', 'typeName', 'code', 'type') + TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Population of inherited members
        self._fields = __class__.fieldnames
        self._has_payload = True
        self._entity_type = cfg.EntityType.Category

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self._json, dict):
                self.data = {key: value for key, value in self._json.items() if key in self.fields}

    def to_string_custom(self):
        """
        Implementation of the abstract method of the class api.TinkAPIResponse

        Generic extended string representation of a TinkAPIResponse instance.

        :return: a formatted, human readable string representation of the data
        within an instance of this class
        """
        text = self.to_string() + os.linesep

        if self._json and isinstance(self._json, list):
            for e in self._json:
                if isinstance(e, dict):
                    for k, v in e.items():
                        if k in CategoryResponse.fieldnames:
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

        request = TinkAPIRequest(method='POST', endpoint=self._url_root + '/api/v1/user/create')

        headers = request.headers
        headers.update({'Authorization': f'Bearer {client_access_token}'})
        headers.update({'Content-Type': 'application/json'})
        request.headers = headers

        body = request.payload
        body.update({'market': market})
        body.update({'locale': locale})
        body.update({'label': label})
        body.update({'external_user_id': ext_user_id})
        request.payload = body

        request.log()

        response = requests.post(url=request.endpoint,
                                 data=json.dumps(request.payload),
                                 headers=request.headers)

        return UserActivationResponse(request, response)

    def delete_user(self, access_token):
        """
        Call the API endpoint /api/v1/user/delete

        Delete an existing user in the Tink platform.

        Hint:
        The access_token can be gathered using the following call sequence
        within the module Categorisation.Tink.model:
        1. client_access_token = authorize_client(scope='user:delete',
                                                  ext_user_id=ext_user_id)
        => ext_user_id is the user that should be deleted.
        2. code = grant_user_access(client_access_token, ext_user_id, scope)
        => ext_user_id is the user for which the information is requested.
        3. access_token = get_oauth_access_token(code, grant_type)

        :param access_token: The OAuth2 user access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.grant_user_access(...)
        :return: A response wrapper object (instance of api.UserDeleteResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='POST', endpoint=self._url_root + '/api/v1/user/delete')

        headers = request.headers
        headers.update({'X-Tink-OAuth-Client-ID': secret.TINK_CLIENT_ID})
        headers.update({'Authorization': f'Bearer {access_token}'})
        headers.update({'Content-Type': 'application/json'})
        request.headers = headers

        request.log()

        response = requests.post(url=request.endpoint,
                                 data=json.dumps(request.payload),
                                 headers=request.headers)

        return UserDeleteResponse(request, response)

    def get_user(self, ext_user_id, access_token):
        """
        Call the API endpoint /api/v1/user

        Get information for an existing user in the Tink platform.

        Hint:
        The access_token can be gathered using the following call sequence
        within the module Categorisation.Tink.model:
        1. client_access_token = model.authorize_client(scope='user:read')
        2. code = grant_user_access(client_access_token, ext_user_id, scope)
        => ext_user_id is the user for which the information is requested.
        3. access_token = get_oauth_access_token(code, grant_type)
        :param ext_user_id: External user reference (this is NOT the Tink internal id).
        :param access_token: The OAuth2 user access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.grant_user_access(...)
        :return: A response wrapper object (instance of api.UserResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='GET', endpoint=self._url_root + '/api/v1/user')
        request.ext_user_id = ext_user_id

        headers = request.headers
        headers.update({'X-Tink-OAuth-Client-ID': secret.TINK_CLIENT_ID})
        headers.update({'Authorization': f'Bearer {access_token}'})
        headers.update({'Content-Type': 'application/json'})
        request.headers = headers

        request.log()

        response = requests.get(url=request.endpoint, headers=request.headers)

        return UserResponse(request, response)

@TinkAPIResponse.register
class UserActivationResponse(TinkAPIResponse):

    """
    Abstract wrapper class for UserActivationResponse from Tink's user service.
    """

    # Define fields/payload of interest referring to the official API documentation
    fieldnames: tuple = ('user_id',) + TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Population of inherited members
        self._fields = __class__.fieldnames
        self._has_payload = False
        self._entity_type = cfg.EntityType.User

        # Custom attributes relevant for this response
        self.user_id = None

        payload = dict()
        payload.update({'userExternalId': str(self.request.ext_user_id)})

        for k, v in self._json.items():
            if k in ('errorMessage', 'errorCode'):
                payload.update({k: v})
            else:
                payload.update({'errorMessage': ''})
                payload.update({'errorCode': ''})
            if k == 'user_id':
                payload.update({k: v})
                self.user_id = v

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
class UserDeleteResponse(TinkAPIResponse):

    """
    Abstract wrapper class for UserDeleteResponse from Tink's user service.
    """

    fieldnames: tuple = TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Population of inherited members
        self._fields = __class__.fieldnames
        self._has_payload = True
        self._entity_type = cfg.EntityType.User

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
class UserResponse(TinkAPIResponse):

    """
    Abstract wrapper class for UserResponse from Tink's user service.
    """

    fieldnames: tuple = data.TinkDAO.fields_user_api_out + TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.

        :param request: Request to the API endpoint - an instance of TinkAPIRequest.
        :param request: Request to the API endpoint - an instance of requests.Response
        """
        try:
            super().__init__(request, response)
        except AttributeError as e:
            raise e

        # Population of inherited members
        self._fields = __class__.fieldnames
        self._has_payload = True
        self._entity_type = cfg.EntityType.User

        payload = dict()
        payload.update({'userExternalId': str(self.request.ext_user_id)})

        # Save fields of interest referring to the official API documentation
        if self.http_status(cfg.HTTPStatusCode.Code2xx) and isinstance(self._json, dict):
            for k, v in self._json.items():
                if k in('errorMessage', 'errorCode'):
                    payload.update({k: v})
                else:
                    payload.update({'errorMessage': ''})
                    payload.update({'errorCode': ''})

                if k == 'created':
                    d = utl.strdate(datetime.fromtimestamp(v/1000))
                    payload.update({k: d})
                elif k == 'id':
                    user_id = v
                    payload.update({k: v})
                elif k == 'profile':
                    profile = v
                    if isinstance(profile, dict):
                        field = 'currency'
                        if field in profile:
                            payload.update({field: profile[field]})
                        field = 'locale'
                        if field in profile:
                            payload.update({field: profile[field]})
                        field = 'market'
                        if field in profile:
                            payload.update({field: profile[field]})
                        field = 'timeZone'
                        if field in profile:
                            payload.update({field: profile[field]})
                if k == 'label':
                    payload.update({k: v})

            self._payload = payload

    def to_string_custom(self):
        """
        Implementation of the abstract method of the class api.TinkAPIResponse.
        Generic extended string representation of a TinkAPIResponse instance.
        :return: A formatted, human readable string representation of the data
        within an instance of this class.
        """
        raise NotImplementedError


class AccountService(TinkAPI):

    """
    Wrapper class for the Tink account service.
    """

    def __init__(self, url_root=cfg.API_URL_TINK_CONNECTOR):
        """
        Initialization.
        """
        super().__init__(url_root)

    def ingest_accounts(self, ext_user_id, accounts: data.TinkEntityList, client_access_token):
        """
        Call the Connector API endpoint users/{{external-user-id}}/accounts

        Ingest a list of accounts into the space of an existing user in the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param accounts: A list of all accounts
        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)

        :return: a response wrapper object (instance of api.AccountIngestionResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        endpoint = self._url_root + f'/users/{ext_user_id}/accounts'
        request = TinkAPIRequest(method='POST', endpoint=endpoint)
        request.ext_user_id = ext_user_id

        headers = request.headers
        headers.update({'Authorization': f'Bearer {client_access_token}'})
        headers.update({'Content-Type': 'application/json'})
        request.headers = headers

        body = request.payload
        user_accounts = accounts.get_entities(ext_user_id=ext_user_id)
        body.update({'accounts': user_accounts})
        request.payload = body

        json_data = json.dumps(request.payload)

        request.log()

        response = requests.post(url=request.endpoint,
                                 data=json_data,
                                 headers=request.headers)

        return AccountIngestionResponse(request, response)

    def list_accounts(self, ext_user_id, access_token):
        """
        Call the API endpoint accounts/list

        Get a list of accounts into the space of an existing user in the Tink platform.

        Hint:
        The access_token can be gathered using the following call sequence
        within the module Categorisation.Tink.model:
        1. client_access_token = model.authorize_client(scope='user:read')
        2. code = grant_user_access(client_access_token, ext_user_id, scope)
        => ext_user_id is the user for which the information is requested.
        3. access_token = get_oauth_access_token(code, grant_type)

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param access_token: The OAuth2 user access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.grant_user_access(...)

        :return: a response wrapper object (instance of api.AccountListResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='GET', endpoint=self._url_root + '/api/v1/accounts/list')
        request.ext_user_id = ext_user_id

        headers = request.headers
        headers.update({'X-Tink-OAuth-Client-ID': secret.TINK_CLIENT_ID})
        headers.update({'Authorization': f'Bearer {access_token}'})
        headers.update({'Content-Type': 'application/json'})
        request.headers = headers

        request.log()

        response = requests.get(url=request.endpoint, headers=request.headers)

        return AccountListResponse(request, response)

@TinkAPIResponse.register
class AccountIngestionResponse(TinkAPIResponse):

    """
    Abstract wrapper class for AccountIngestionResponse from Tink's account service.
    """

    fieldnames = TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Population of inherited members
        self._fields = __class__.fieldnames
        self._has_payload = False
        self._entity_type = cfg.EntityType.Account

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

    fieldnames = data.TinkDAO.fields_acc_api_out + TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        try:
            super().__init__(request, response)
        except AttributeError as e:
            raise e

        # Population of inherited members
        self._fields = __class__.fieldnames
        self._has_payload = True
        self._entity_type = cfg.EntityType.Account

        payload = list()
        item = dict()

        if self.http_status(cfg.HTTPStatusCode.Code2xx) and isinstance(self._json, dict):
            key = 'accounts'
            if key in self._json:
                accounts = self._json[key]

                for account in accounts:
                    item.update({'userExternalId': str(self.request.ext_user_id)})
                    for field in self.fields:
                        if field in account:
                            item.update({field: account[field]})
                        elif field in ('errorMessage', 'errorCode'):
                            item.update({'errorMessage': ''})
                            item.update({'errorCode': ''})

                    payload.append(item)

                self._payload = payload

    def to_string_custom(self):
        """
        Implementation of the abstract method of the class api.TinkAPIResponse.
        Generic extended string representation of a TinkAPIResponse instance.
        :return: A formatted, human readable string representation of the data
        within an instance of this class.
        """
        text = self.to_string() + os.linesep

        if self._json and isinstance(self._json, list):
            for e in self._json:
                if isinstance(e, dict):
                    for k, v in e.items():
                        if k in self.names:
                            text += str(k) + ':' + str(v)[0:cfg.UI_STRING_MAX_WITH] + ', '
        else:
            text += self.to_string_formatted()

        return str(text)


class TransactionService(TinkAPI):

    """
    Wrapper class for the Tink transaction service.
    """

    def __init__(self, url_root=cfg.API_URL_TINK_CONNECTOR):
        """
        Initialization.
        """
        super().__init__(url_root)

    def ingest_transactions(self,
                            ext_user_id,
                            accounts: data.TinkEntityList,
                            transactions: data.TinkEntityList,
                            client_access_token):
        """
        Call the Connector API endpoint users/{{external-user-id}}/accounts

        Ingest a list of accounts into the space of an existing user in the Tink platform.

        :param ext_user_id: external user reference (this is NOT the Tink internal id)
        :param accounts: A list of all accounts
        :param transactions: A list of all transactions
        :param client_access_token: The client access token gathered via the endpoint
        /api/v1/oauth/token which can be called using OAuthService.authorize_client_access(...)

        :return: a response wrapper object (instance of api.AccountIngestionResponse)
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        endpoint = self._url_root + f'/users/{ext_user_id}/transactions'
        request = TinkAPIRequest(method='POST', endpoint=endpoint)
        request.ext_user_id = ext_user_id

        headers = request.headers
        headers.update({'Authorization': f'Bearer {client_access_token}'})
        headers.update({'Content-Type': 'application/json'})
        request.headers = headers

        body = request.payload
        account_data = accounts.get_entities()
        trx_data = transactions.get_entities()
        key = 'transactionAccounts'
        body.update({key: account_data})
        for item in body[key]:
            item.transactions = trx_data
        # TODO: Add 'type': REAL_TIME|HISTORICAL|BATCH as a parameter of ingest_transactions()
        body.update({'type': 'REAL_TIME'})
        request.payload = body

        json_data = json.dumps(request.payload)

        request.log()

        response = requests.post(url=request.endpoint,
                                 data=json_data,
                                 headers=request.headers)

        return AccountIngestionResponse(request, response)


@TinkAPIResponse.register
class TransactionIngestionResponse(TinkAPIResponse):

    """
    Abstract wrapper class for AccountIngestionResponse from Tink's account service.
    """

    fieldnames = TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Population of inherited members
        self._fields = __class__.fieldnames
        self._has_payload = False
        self._entity_type = cfg.EntityType.Transaction

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

    def authorize_client_access(self, grant_type, scope, ext_user_id=None):
        """
        Call the API endpoint /api/v1/oauth/token

        Authorize access to the client (company account).

        This method will gather an access token (valid only for the authenticated client)
        that can be used to manipulate the users tied to TINK_CLIENT_ID.
        The access token usually expires after 30 mins and can be renewed with an
        appropriate refresh token that should also be kept as a secret (like the client secret)

        :param grant_type: The grant type.
        Values: authorization_code, refresh_token, client_credentials
        :param scope: The requested scope when using client credentials.
        :param ext_user_id: The external user reference (this is NOT the Tink internal id)
        If provided then the service has to be used to authorize deletion of a user.
        This is a workaround (provided by Tink) that can be used in order
        to delete existing users

        :return: OAuth2AuthenticationTokenResponse
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        request = TinkAPIRequest(method='POST', endpoint=self._url_root + '/api/v1/oauth/token')

        body = request.payload
        body.update({'scope': scope})
        if ext_user_id:
            body.update({'ext_user_id': ext_user_id})
        body.update({'client_id': secret.TINK_CLIENT_ID})
        body.update({'client_secret': secret.TINK_CLIENT_SECRET})
        body.update({'grant_type': grant_type})
        request.payload = body

        request.log()

        response = requests.post(url=request.endpoint, data=request.payload)

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

        request = TinkAPIRequest(method='POST', endpoint=self._url_root + '/api/v1/oauth/authorization-grant')

        headers = request.headers
        headers.update({'Authorization': f'Bearer {client_access_token}'})
        request.headers = headers

        body = request.payload
        body.update({'scope': scope})
        if user_id:
            body.update({'user_id': user_id})
        elif ext_user_id:
            body.update({'external_user_id': ext_user_id})

        request.log()

        response = requests.post(url=request.endpoint,
                                 data=request.payload,
                                 headers=request.headers)

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

        request = TinkAPIRequest(method='POST', endpoint=self._url_root + '/api/v1/oauth/token')

        body = request.payload
        body.update({'code': code})
        body.update({'client_id': secret.TINK_CLIENT_ID})
        body.update({'client_secret': secret.TINK_CLIENT_SECRET})
        body.update({'grant_type': grant_type})

        request.log()

        response = requests.post(url=request.endpoint, data=request.payload)

        return OAuth2AuthenticationTokenResponse(request, response)


@TinkAPIResponse.register
class OAuth2AuthenticationTokenResponse(TinkAPIResponse):

    """
    Abstract wrapper class for a AuthenticationResponse from Tink's OAuth service.
    """

    fieldnames = 'access_token', 'token_type', 'expires_in', 'scope', 'id_hint'

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

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self._json, dict):
                self.data = {key: value for key, value in self._json.items()
                             if key in OAuth2AuthenticationTokenResponse.fieldnames}
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

    fieldnames = ('code',) + TinkAPIResponse.fieldnames

    def __init__(self, request, response):
        """
        Initialization.
        """
        super().__init__(request, response)

        # Custom attributes relevant for this response
        self.code = None

        # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
        self.data = {key: value for key, value in self._json.items()
                     if key in OAuth2AuthorizeResponse.fieldnames}

        # Save fields of interest referring to the official API documentation
        if isinstance(response, requests.Response) and response.status_code == 200:
            if isinstance(self._json, dict):
                self.data = {key: value for key, value in self._json.items()
                             if key in OAuth2AuthorizeResponse.fieldnames}
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

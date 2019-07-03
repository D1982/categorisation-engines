"""Direct access to Tink's API endpoints. """

import Categorisation.Common.config as cfg
import Categorisation.Common.secret as secret

import os
import sys
import collections
import logging
import requests
import json

"""TinkAPI class."""


class TinkAPI:
    def __init__(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.url_root = cfg.API_URL_TINK
        self.service_group = None
        self.service = None
        self.last_call_url = None

        self.partner_info = dict()
        self.partner_info['client_id'] = secret.TINK_CLIENT_ID
        self.partner_info['client_secret'] = secret.TINK_CLIENT_SECRET


"""Abstract wrapper class for a request to the Tink API."""


class TinkAPIRequest:
    def __init__(self, method, endpoint):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        self.method = method
        self.endpoint = endpoint
        self.headers = collections.OrderedDict()
        self.data = collections.OrderedDict()
        self.names = collections.OrderedDict()

    def to_string(self):
        return 'REQUEST: {m} {t}'.format(m=self.method, t=self.endpoint)

    def to_string_formatted(self):
        text = self.to_string()

        text += os.linesep*2 + '*** Header ***:'
        for k, v in self.headers.items():
            text += os.linesep + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        text += os.linesep*2 + '*** Body ***:'
        for k, v in self.data.items():
            text += os.linesep + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        return text

    # Abstract Methods
    def to_string_custom(self):
        pass


"""Abstract wrapper class for a response object of the Python requests library."""


class TinkAPIResponse:
    def __init__(self, response):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Data from requests.Response object
        self.text = response.text or ''
        self.content = response.content or '{}'
        self.content_text = str(response.content) or ''
        self.status_code = response.status_code or -1
        self.reason = response.reason or ''

        # Data to be populated by sub-classes
        self.names = collections.OrderedDict()
        self.data = collections.OrderedDict()
        self.json = dict()

        # Response JSON
        try:
            self.json = response.json() or dict()
        except Exception as e:
            logging.warning("Warning:{0}".format(e.args or ""))#
            # This service does not return a JSON so just use the text instead
            self.data.update({'text': response.text})

    """Minimalistic string representation of a TinkAPIResponse instance."""
    def to_string(self):
        return 'RESPONSE: ' + self.reason + ' ({code})'.format(code=str(self.status_code))

    """Extended string representation of a TinkAPIResponse instance."""
    def to_string_formatted(self):
        text = self.to_string()

        if self.json:
            for k, v in self.json.items():
                text += os.linesep + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        if self.data:
            for k, v in self.data.items():
                text += os.linesep + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        return text + os.linesep*2

    """Abstract method."""
    def to_string_custom(self):
        pass


"""Wrapper class for the Tink monitoring service."""


class MonitoringService(TinkAPI):
    def __init__(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__()

    def ping(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'GET'
        postfix = '/api/v1/monitoring/ping'
        # Request headers
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        # Log Request
        logging.debug('POST {dest}'.format(
                dest=req.endpoint, data=req.data))
        # Fire the request against the API endpoint
        response = requests.get(url=req.endpoint)
        # Process the response
        resp = TinkAPIResponse(response)

        return req, resp

    def health_check(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'GET'
        postfix = '/api/v1/monitoring/healthy'
        # Request headers
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        # Log Request
        logging.debug('POST {dest}'.format(
                dest=req.endpoint))
        # Fire the request against the API endpoint
        response = requests.get(url=req.endpoint)
        # Process the response
        resp = TinkAPIResponse(response)
        return req, resp


"""Wrapper class for the Tink category service."""


class CategoryService(TinkAPI):
    def __init__(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__()

    def list_categories(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'GET'
        postfix = '/api/v1/categories'
        # Request headers
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        # Log Request
        logging.debug('POST {dest}'.format(
                dest=req.endpoint))
        # Fire the request against the API endpoint
        response = requests.get(url=req.endpoint)
        # Process the response
        resp = TinkAPIResponse(response)
        return req, resp


"""Wrapper class for the Tink user service."""


class UserService(TinkAPI):
    def __init__(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__()

    """Create a new user in the Tink platform."""
    def activate_user(self, ext_user_id, label, market, locale, client_access_token):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'POST'
        postfix = '/api/v1/user/create'
        # Request headers
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        req.headers.update({'Authorization': 'Bearer ' + client_access_token})
        req.headers.update({'Content-Type': 'application/json'})
        # Request body
        req.data.update({'external_user_id': ext_user_id})
        #req.data.update({'label': label})
        req.data.update({'market': market})
        req.data.update({'locale': locale})
        # Log Request
        logging.debug('POST {dest} using data {data}'.format(
                dest=req.endpoint, data=req.data))
        # Fire the request against the API endpoint
        response = requests.post(url=req.endpoint, data=json.dumps(req.data), headers=req.headers)
        # Process the response
        resp = UserActivationResponse(response)
        # Log the result depending on the HTTP status code
        if resp.content and resp.status_code == 204:
            logging.debug('RESPONSE from {dest} Response => {data}'.format(
                    dest=req.endpoint, data=str(resp.to_string())))
        else:
            logging.debug('RESPONSE from {dest} not as expected => {msg}'.format(
                    dest=req.endpoint, msg=resp.to_string()))

        return req, resp


    """Delete an existing user in the Tink platform."""
    def delete_user(self, user_id, ext_user_id, client_access_token):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'POST'
        postfix = '/api/v1/user/delete'
        # Request headers
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        req.headers.update({'X-Tink-OAuth-Client-ID': secret.TINK_CLIENT_ID})
        req.headers.update({'Authorization': 'Bearer ' + client_access_token})
        # Request body remains empty

        # Log Request
        logging.debug('POST {dest} using data {data}'.format(
                dest=req.endpoint, data=req.data))
        # Fire the request against the API endpoint
        response = requests.post(url=req.endpoint, data=json.dumps(req.data), headers=req.headers)
        # Process the response
        resp = UserDeleteResponse(response)
        # Log the result depending on the HTTP status code
        if resp.content and resp.status_code == 204:
            logging.debug('RESPONSE from {dest} Response => {data}'.format(
                    dest=req.endpoint, data=str(resp.to_string())))
        else:
            logging.debug('RESPONSE from {dest} not as expected => {msg}'.format(
                    dest=req.endpoint, msg=resp.to_string()))

        return req, resp


"""Wrapper class for the Tink OAuth service."""


class OAuthService(TinkAPI):
    def __init__(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__()

    """Authorize access to the client (company account).
    
    https://docs.tink.com/enterprise/api/#get-an-authorization-token
    
    This method will store an access token (valid only for the authenticated client) 
    that can be used to manipulate the users tied to secret.TINK_CLIENT_ID. 
    The access token usually expires after 30 mins and can be renewed with an
    appropriate refresh token that should also be kept as a secret (like the client secret)
    """
    def authorize_client_access(self, grant_type, scope, delete_dict=None):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'POST'
        postfix = '/api/v1/oauth/token'

        # Prepare the request
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        req.data.update({'client_id': secret.TINK_CLIENT_ID})
        req.data.update({'client_secret': secret.TINK_CLIENT_SECRET})
        req.data.update({'grant_type': grant_type})
        req.data.update({'scope': scope})

        # If delete_dict is provided then the service has to be used to delete data
        # This is a workaround that can be used in order to delete existing users and accounts
        if delete_dict:
            if 'external_user_id' in delete_dict:
                req.data.update({'external_user_id': delete_dict['external_user_id']})
            elif 'user_id' in delete_dict:
                req.data.update({'user_id': delete_dict['user_id']})
        #TODO: Add accounts in case of deletion for accounts is also working

        # Log Request
        logging.debug('POST {dest} using data {data}'.format(
                dest=req.endpoint, data=req.data))
        # Fire the request against the API endpoint
        response = requests.post(url=req.endpoint, data=req.data)
        # Process the response
        resp = OAuth2AuthenticationTokenResponse(response)
        # Log the result depending on the HTTP status code
        if resp.content and resp.status_code == 200:
            logging.debug('RESPONSE from {dest} Response => {data}'.format(
                    dest=req.endpoint, data=str(resp.to_string())))
        else:
            logging.debug('RESPONSE from {dest} not as expected => {msg}'.format(
                    dest=req.endpoint, msg=resp.to_string()))

        return req, resp

    """Grant access to a user.
    
    https://docs.tink.com/enterprise/api/#create-an-authorization-for-the-given-user-id-with-requested-scopes
    """
    def grant_user_access(self, client_access_token, user_id, ext_user_id, scope='user:read'):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'POST'
        postfix = '/api/v1/oauth/authorization-grant'

        # Prepare the request
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        req.headers.update({'Authorization: Bearer': client_access_token})
        req.data.update({'client_access_token': client_access_token})
        req.data.update({'user_id': user_id})
        req.data.update({'external_user_id': ext_user_id})
        req.data.update({'scope': scope})

        # Log Request
        logging.debug('POST {dest} using data {data}'.format(
                dest=req.endpoint, data=req.data))
        # Fire the request against the API endpoint
        response = requests.post(url=req.endpoint, data=req.data)
        # Process the response
        resp = OAuth2AuthorizeResponse(response)
        # Log the result depending on the HTTP status code
        if resp.content and resp.status_code == 200:
            logging.debug('RESPONSE from {dest} Response => {data}'.format(
                    dest=req.endpoint, data=str(resp.to_string())))
        else:
            logging.debug('RESPONSE from {dest} not as expected => {msg}'.format(
                    dest=req.endpoint, msg=resp.to_string()))

        return req, resp

    """Get the OAuth access token for a user.
    
    ​https://api.tink.se/api/v1/oauth/token
    """
    def get_oauth_access_token(self, code, ):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Target API specifications
        url = self.url_root
        method = 'POST'
        postfix = '/api/v1/oauth/token'

        # Prepare the request
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        req.headers.update({'Authorization: Bearer': client_access_token})
        req.data.update({'client_access_token': client_access_token})
        req.data.update({'user_id': user_id})
        req.data.update({'external_user_id': ext_user_id})
        req.data.update({'scope': scope})

        # Log Request
        logging.debug('POST {dest} using data {data}'.format(
                dest=req.endpoint, data=req.data))
        # Fire the request against the API endpoint
        response = requests.post(url=req.endpoint, data=req.data)
        # Process the response
        resp = OAuth2AuthorizeResponse(response)
        # Log the result depending on the HTTP status code
        if resp.content and resp.status_code == 200:
            logging.debug('RESPONSE from {dest} Response => {data}'.format(
                    dest=req.endpoint, data=str(resp.to_string())))
        else:
            logging.debug('RESPONSE from {dest} not as expected => {msg}'.format(
                    dest=req.endpoint, msg=resp.to_string()))

        return req, resp


"""Abstract wrapper class for a AuthenticationResponse from Tink's OAuth service."""
# TODO: Check if there might be a better naming for this class

class OAuth2AuthenticationTokenResponse(TinkAPIResponse):

    def __init__(self, response):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'access_token', 'token_type', 'expires_in', 'scope', 'errorMessage', 'errorCode'}
        # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
        self.data = {key: value for key, value in self.json.items() if key in self.names}


"""Abstract wrapper class for a AuthorizeResponse from Tink's OAuth service."""
# TODO: Check if there might be a better naming for this class

class OAuth2AuthorizeResponse(TinkAPIResponse):

    def __init__(self, response):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'code', 'errorMessage', 'errorCode'}
        # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
        self.data = {key: value for key, value in self.json.items() if key in self.names}

        # Save relevant data in dedicated member variables => Facilitates data flow
        if self.status_code == 200:
            self.scope = self.data['code']


"""Abstract wrapper class for UserActivationResponse from Tink's user service."""


class UserActivationResponse(TinkAPIResponse):

    def __init__(self, response):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'user_id', 'errorMessage', 'errorCode'}

        # Save relevant data in dedicated member variables => Facilitates data flow
        if self.status_code == 204:
            self.user_id = self.data['user_id']

            # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
            self.data = {key: value for key, value in self.json.items() if key in self.names}


"""Abstract wrapper class for UserDeleteResponse from Tink's user service."""


class UserDeleteResponse(TinkAPIResponse):

    def __init__(self, response):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'user_id', 'errorMessage', 'errorCode'}

        # Save relevant data in dedicated member variables => Facilitates data flow
        if self.status_code == 204:
            self.user_id = self.data['user_id']

            # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
            self.data = {key: value for key, value in self.json.items() if key in self.names}
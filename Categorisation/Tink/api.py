""" Tink API

"""
import Categorisation.Common.config as cfg
import Categorisation.Common.secret as secret

import os
import collections
import logging
import requests
import json

class TinkAPI:
    def __init__(self):
        self.url_root = cfg.API_URL_TINK
        self.service_group = None
        self.service = None
        self.last_call_url = None

        self.partner_info = dict()
        self.partner_info['client_id'] = secret.TINK_CLIENT_ID
        self.partner_info['client_secret'] = secret.TINK_CLIENT_SECRET


class TinkAPIRequest:
    def __init__(self, method, endpoint):
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


""" Abstract wrapper class for a Tink Response requests.Response object
"""
class TinkAPIResponse:
    def __init__(self, response):
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

    def to_string(self):
        return 'RESPONSE: ' + self.reason + ' ({code})'.format(code=str(self.status_code))

    def to_string_formatted(self):
        text = self.to_string()

        if self.json:
            for k, v in self.json.items():
                text += os.linesep + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        if self.data:
            for k, v in self.data.items():
                text += os.linesep + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        return text + os.linesep*2

    # Abstract Methods
    def to_string_custom(self):
        pass


class MonitoringService(TinkAPI):
    def __init__(self):
        super().__init__()

    def ping(self):
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

class CategoryService(TinkAPI):
    def __init__(self):
        super().__init__()

    def list_categories(self):
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


class UserService(TinkAPI):
    def __init__(self):
        super().__init__()

    def activate_user(self, ext_user_id, label, market, locale, client_access_token):
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

    def delete_user(self, ext_user_id):
        pass

    def get_user(self, ext_user_id):
        # Target API specifications
        url = self.url_root
        method = 'GET'
        postfix = '/api/v1/user'

class OAuthService(TinkAPI):
    def __init__(self):
        super().__init__()

    """ 
    Authorize access to the client (company account) 
    Documentation: https://docs.tink.com/enterprise/api/#get-an-authorization-token
    Purpose​: This will return an API token (valid only for the authenticated client) 
             that can be used to manipulate the users tied to your clientId. 
             Remember that your YOUR_CLIENT_SECRET should be kept a secret!
    Response​: ​Access Token Response for a client which expires after 30 mins 
             (no refresh token provided, use the same endpoint again to get a 
             new access token). Please note that this token must also be kept a 
             secret and not exposed to any public client.

    """
    def authorize_client_access(self, grant_type, scope):
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



    """ 
    Grant access to a user 
    https://docs.tink.com/enterprise/api/#create-an-authorization-for-the-given-user-id-wit h-requested-scopes
    """
    def grant_user_access(self, client_access_token, user_id, ext_user_id, scope='user:read'):
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

    """ 
    Get the OAuth access token 
    ​https://api.tink.se/api/v1/oauth/token
    """
    def get_oauth_access_token(self, code, ):
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

class OAuth2AuthenticationTokenResponse(TinkAPIResponse):

    def __init__(self, response):
        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'access_token', 'token_type', 'expires_in', 'scope', 'errorMessage', 'errorCode'}
        # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
        self.data = {key: value for key, value in self.json.items() if key in self.names}


class OAuth2AuthorizeResponse(TinkAPIResponse):

    def __init__(self, response):
        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'code', 'errorMessage', 'errorCode'}
        # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
        self.data = {key: value for key, value in self.json.items() if key in self.names}

        # Save relevant data in dedicated member variables => Facilitates data flow
        if self.status_code == 200:
            self.scope = self.data['code']


class UserActivationResponse(TinkAPIResponse):

    def __init__(self, response):
        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'user_id', 'errorMessage', 'errorCode'}

        # Save relevant data in dedicated member variables => Facilitates data flow
        if self.status_code == 204:
            self.user_id = self.data['user_id']

            # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
            self.data = {key: value for key, value in self.json.items() if key in self.names}
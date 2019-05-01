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


    def service_url(self, service, remember=True):
        url = self.url_root + self.service_group + service
        if remember:
            self.last_call_url = url
        return url


class TinkAPIRequest:
    def __init__(self, method, endpoint):
        self.method = method
        self.endpoint = endpoint
        self.headers = collections.OrderedDict()
        self.data = collections.OrderedDict()
        self.names = collections.OrderedDict()

    def to_string(self):
        return '{m} {t}'.format(m=self.method, t=self.endpoint)

    def to_string_formatted(self):
        text = self.to_string()
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
        self.content = response.content or '{}'
        self.content_text = str(response.content)
        self.status_code = response.status_code or -1
        self.reason = response.reason or ''
        self.json = response.json() or dict()

        # Additional data to be populated by sub-classes
        self.names = collections.OrderedDict()
        self.data = collections.OrderedDict()

    def to_string(self):
        return 'RESPONSE ' + self.reason + ' ({code})'.format(code=str(self.status_code))

    def to_string_formatted(self):
        text = self.to_string()
        for k, v in self.data.items():
            text += os.linesep + str(k) + ': ' + str(v)[0:cfg.UI_STRING_MAX_WITH]

        return text

    # Abstract Methods
    def to_string_custom(self):
        pass


class MonitoringService(TinkAPI):
    def __init__(self):
        super().__init__()
        self.service_group = '/api/v1/monitoring/'

    def ping(self):
        response = requests.get(url=self.service_url('ping'))
        content = response.content
        return content

    def health_check(self):
        response = requests.get(url=self.service_url('healthy'))
        content = response.content
        return content

class CategoryService(TinkAPI):
    def __init__(self):
        super().__init__()

    def list_categories(self):
        self.service_group = '/api/v1/monitoring/'
        endpoint = self.url_root + '/api/v1/oauth/authorization-grant'
        response = requests.get(url=self.url + '/api/v1/categories')
        content = response.content
        return content


class UserService(TinkAPI):
    def __init__(self):
        super().__init__()

    def activate_user(self):
        pass


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
    def authorize_client_access(self, client_access_token, user_id,
                                scope='accounts:read,transactions:read,user:read'):
        # Target API specifications
        url = self.url_root
        method = 'POST'
        postfix = '/api/v1/oauth/token'

        # Prepare the request
        req = TinkAPIRequest(method=method, endpoint=url+postfix)
        req.headers.update({'Authorization: Bearer': client_access_token})
        req.data.update({'client_access_token': client_access_token})
        req.data.update({'user_id': user_id})
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
        req.data.update({'client_id': client_id})
        req.data.update({'client_secret': client_secret})
        req.data.update({'grant_type': grant_type})
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
    ​https://docs.tink.com/api/#exchange-access-tokens
    """
    def get_user_oauth_access_token(self, ):
        pass


class OAuth2AuthenticationTokenResponse(TinkAPIResponse):

    def __init__(self, response):
        super().__init__(response)

        # Define fields of interest referring to the official API documentation
        self.names = {'access_token', 'token_type', 'expires_in', 'scope', 'errorMessage', 'errorCode'}
        # Get relevant data out of the JSON => Facilitates string formatting for UI outputs
        self.data = {key: value for key, value in self.json.items() if key in self.names}

        # Save relevant data in dedicated member variables => Facilitates data flow
        if self.status_code == 200:
            self.access_token = self.data['access_token']
            self.token_type = self.data['token_type']
            self.expires_in = self.data['expires_in']
            self.scope = self.data['scope']


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
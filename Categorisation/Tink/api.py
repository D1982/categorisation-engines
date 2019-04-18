""" Tink API

"""
import Categorisation.Common.config as cfg
import Categorisation.Common.secret as secret

import requests
import json


class TinkAPI():
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
    def authorize_client_access(self, client_id, client_secret,
                                grant_type='client_credentials',
                                scope='accounts:read,transactions:read,user:read'):

        endpoint = self.url_root + '/api/v1/oauth/authorization-grant'

        payload = dict()
        payload.update({'client_id': client_id, 'client_secret': client_secret})
        payload.update({'grant_type': grant_type})
        payload.update({'scope': scope})

        response = requests.post(url=endpoint, data=json.dumps(payload))
        content = response.content
        if content:
            result = json.loads(str(content) or '')
            access_token = response_dict['access_token']
            token_type = response_dict['token_type']
            expires_in = response_dict['expires_in']
            scope = response_dict['scope']

        else:
            result = response.reason + ' ({c})'.format(c=str(response.status_code))

        return result

    """ 
    Grant access to a user 
    https://docs.tink.com/enterprise/api/#create-an-authorization-for-the-given-user-id-wit h-requested-scopes
    """
    def grant_user_access(self, client_access_token, user_id, scope='user:read'):
        pass

    """ 
    Get the OAuth access token 
    ​https://docs.tink.com/api/#exchange-access-tokens
    """
    def get_user_oauth_access_token(self, ):
        pass
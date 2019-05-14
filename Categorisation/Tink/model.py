import Categorisation.Tink.api as api
import Categorisation.Tink.data as data
import Categorisation.Common.secret as sec

import logging
import os

class TinkModel:

    def __init__(self, dao):
        logging.info("Initiated:" + "TinkModel.__init__()")
        self.dao = dao

    def test_connectivity(self):
        s = api.MonitoringService()

        (request1, response1) = s.ping()
        result1 = request1.to_string_formatted() + os.linesep*2 + response1.to_string_formatted()

        (request2, response2) = s.health_check()
        result2 = request2.to_string_formatted() + os.linesep*2 + response2.to_string_formatted()

        return result1 + os.linesep*2 + result2

    def authentication(self):
        # Set input parameters
        grant_type = 'client_credentials'
        scope = 'authorization:grant,user:create,user:read'
        # Call API
        s = api.OAuthService()
        (request, response) = s.authorize_client_access(grant_type=grant_type, scope=scope)
        # Save output parameters in dedicated member variables => Facilitates data flow

        if response.status_code == 200:
            self.access_token= response.data['access_token']
            self.token_type = response.data['token_type']
            self.expires_in = response.data['expires_in']
            self.scope = response.data['scope']

        return request.to_string_formatted() + os.linesep*2 + response.to_string_formatted()

    def activate_users(self):
        self.dao.read_users()
        self.authentication()
        svc = api.UserService()
        # TODO: Remove hard coded parameters and replace by DAO access
        (request, response) = svc.activate_user(
                ext_user_id='42', locale='UK', market='en_UK', client_access_token=self.client_access_token)
        return request.to_string_formatted() + os.linesep*2 + response.to_string_formatted()

    def delete_users(self):
        # TODO: Remove hard coded parameters and replace by     DAO access
        # Users currently in platform:
        # ext_user_id: 42 => user_id: 7ccf20dd556945ae91febe31a8cb155b
        # ext_user_id: 42 => user_id: 8b9ddbe02c234f39bf8a581eb300f09a
        # ext_user_id: 43 => user_id: ca73adc9e4624ab285c7c203f8192722
        svc = api.UserService()
        (request, response) = svc.delete_user(42)
        return request.to_string_formatted() + os.linesep*2 + response.to_string_formatted()

    def get_categories(self):
        service = api.CategoryService()
        return service.list_categories()
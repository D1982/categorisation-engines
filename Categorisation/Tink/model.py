import Categorisation.Tink.api as api
import Categorisation.Tink.data as data
import Categorisation.Common.secret as sec

import logging
import os

class TinkModel:

    def __init__(self, dao):
        logging.info("Initiated:" + "TinkModel.__init__()")
        self.dao = dao

        self.access_token = ''
        self.token_type = ''
        self.expires_in = ''
        self.scope = ''

    # Read test data from files
    def read_user_data(self):
        return self.dao.read_users()

    def read_account_data(self):
        return self.dao.read_accounts()

    def read_transaction_data(self):
        return self.dao.read_transactions()

    # Health checks
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

    def activate_user(self, ext_user_id, label, market, locale):
        # Instantiate API wrapper
        svc = api.UserService()

        # Fire request and catch both the complete request and the response
        (request, response) = svc.activate_user(
            ext_user_id=ext_user_id, label=label, market=market, locale=locale, client_access_token=self.access_token)

        # Return a summarized string - in that case for the UI console
        return request.to_string_formatted() + os.linesep*2 + response.to_string_formatted()

    """Create users in the Tink platform
    Reads users from a DAO, gets an access token from Tink's API and creates all users
    Hints: 
    1. At the moment there is only one authentication step meaning if the token
    would expire due to longer runtime the current implementation would fail.
    
    2. It is clear that it would be more efficient to use one single API wrapper
    """
    def activate_users(self):
        # Get user data
        users = self.dao.read_users()

        # Get an access token
        self.authentication() # TODO: Check whether access token is still valid instead of doing too much API calls

        # Create all users
        result = ''
        for e in users:
            ext_user_id = e['external_user_id']
            label = e['label']
            market = e['market']
            locale = e['locale']

            result += self.activate_user(ext_user_id, label, market, locale)

        return result

    """Get Users
    SJ (Tink): The short answer is that you cannot get back the external_user_id from the API(!)
    But instead of granting access to the user_id you can instead use the
    {{host}}/api/v1/oauth/authorization-grant
    with
    scope=accounts:read,transactions:read,statistics:read,user:read,investments:read,credentials:write,credentials:read,credentials:refresh,user:delete& *external_user_id=your_external_id* (edited)
    """
    def get_user(self):
        pass

    """Delete Users
    """
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
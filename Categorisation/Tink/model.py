"""Facade to the core categorisation process offered by Tink.

The implementation covers the implementation of a MVP client application.
"""

import Categorisation.Tink.api as api


import logging
import os
import sys

""" The model class is a facade for the functionality typically required in a PoC.

All methods within this class should only be invoked by either instances of ui.TinkUI or by instas of 
this class (model.TinkModel) itself.
Communication with the UI does happen by returning the summarized logs which the UI can then 
print appropriately to the output.
"""


class TinkModel:

    def __init__(self, dao):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Data Access Object
        self.dao = dao

        # Settings (will be set by instances of class TinkUI)
        self.delete_flag = False  # Flag whether to pre-delete existing data
        self.proxy_usage_flag = False  # Flag whether to use a http proxy

        # Variables
        self.access_token = ''
        self.token_type = ''
        self.expires_in = ''
        self.scope = ''

        # Latest Request/Response
        self.request = None
        self.response = None


    # Read test data from files
    def read_user_data(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        return self.dao.read_users()

    def read_account_data(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        return self.dao.read_accounts()

    def read_transaction_data(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        return self.dao.read_transactions()

    """Test the API connectivity."""
    def test_connectivity(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        s = api.MonitoringService()

        (request1, response1) = s.ping()
        result1 = request1.to_string_formatted() + os.linesep*2 + response1.to_string_formatted()

        (request2, response2) = s.health_check()
        result2 = request2.to_string_formatted() + os.linesep*2 + response2.to_string_formatted()

        result_log += result1 + os.linesep*2 + result2

        return result_log

    """Authorize the client (Tink customer account)."""
    def authorize_client(self, grant_type='client_credentials', scope='authorization:grant', ):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Call API
        s = api.OAuthService()
        (request, response) = s.authorize_client_access(grant_type=grant_type, scope=scope)

        # Save output parameters in dedicated member variables => Facilitates data flow
        if response.status_code == 200:
            self.access_token= response.data['access_token']
            self.token_type = response.data['token_type']
            self.expires_in = response.data['expires_in']
            self.scope = response.data['scope']

            # Save the request/response
            self.request = request
            self.response = response

        result_log += request.to_string_formatted() + os.linesep*2 + response.to_string_formatted()
        return result_log


    """Authorize the client (Tink customer account) to delete an object in the Tink platform.
    
    This is to be considered as a workaround resp. the only way to delete an existing user.
    """
    def authorize_client_delete(self, grant_type='client_credentials', scope='user:delete', delete_dict=None):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        if not delete_dict:
            msg = 'Method authorize_client_delete() was invoked without data to be deleted'
            logging.warning(msg)
            return msg

        if 'user_id' in delete_dict:
            key = 'user_id'
            value = delete_dict[key]
        elif 'external_user_id' in delete_dict:
            key = 'external_user_id'
        #TODO: Add accounts in case of deletion for accounts is also working

        msg = 'Trying to delete {k}:{v} '.format(k=key, v=value)
        logging.info(msg)
        result_log += msg
        # Call API
        s = api.OAuthService()
        (request, response) = s.authorize_client_access(grant_type, scope, delete_dict)
        # Save output parameters in dedicated member variables => Facilitates data flow

        if response.status_code == 204:
            msg = 'Successfully deleted {k}:{v} '.format(k=key, v=value)
        elif response.status_code == 404:
            msg = 'Object does not exist - {k}:{v} '.format(k=key, v=value)

        # Save the request/response
        self.request = request
        self.response = response

        logging.info(msg)
        result_log += msg
        result_log += request.to_string_formatted() + os.linesep * 2 + response.to_string_formatted()

        return result_log

    """Initiates the creation of multiple users in the Tink platform.
    
    Reads users from a DAO, gets an access token from Tink's API and creates all users
    Hints: 
    1. At the moment there is only one authentication step meaning if the token
    would expire due to longer runtime the current implementation would fail.
    
    2. It is clear that it would be more efficient to use one single API wrapper
    """
    def activate_users(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Get user data
        users = self.dao.read_users()
        #  Authorize client to create users
        result_log += self.authorize_client(scope='user:create')
        # Iterate all users
        for e in users:
            ext_user_id = e['external_user_id']
            label = e['label']
            market = e['market']
            locale = e['locale']
            # Create the user
            result_log += self.activate_user(ext_user_id, label, market, locale, self.access_token)

        return result_log

    """Initiates the creation of a single user in the Tink platform."""
    def activate_user(self, ext_user_id, label, market, locale, client_access_token):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Make sure that there is a valid client_access_token available
        if not client_access_token:
            result_log += self.authorize_client(scope='user:create')
            client_access_token = self.access_token

        # Instantiate API wrapper of the user service
        svc = api.UserService()
        # Fire request and catch both the complete request and the response
        (request, response) = svc.activate_user(ext_user_id, label, market, locale, client_access_token)

        # Save the request/response
        self.request = request
        self.response = response

        result_log += request.to_string_formatted() + os.linesep*2 + response.to_string_formatted()
        # Return a summarized string - in that case for the UI console

        return result_log

    """Get Users
    SJ (Tink): The short answer is that you cannot get back the external_user_id from the API(!)
    But instead of granting access to the user_id you can instead use the
    {{host}}/api/v1/oauth/authorization-grant
    with
    scope=accounts:read,transactions:read,statistics:read,user:read,investments:read,credentials:write,credentials:read,credentials:refresh,user:delete& *external_user_id=your_external_id* (edited)
    """
    def user_exists(self, user_id=None, external_user_id=None):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        if user_id:
            delete_dict = {'user_id': user_id}
        elif external_user_id:
            delete_dict = {'external_user_id': user_id}

        result_log += self.authorize_client(scope='user:delete', delete_dict=delete_dict)

        if self.response == 404:
            return False
        elif self.response == 204:
            return True
        else:
            return False

    """Delete users in the Tink platform."""
    def delete_users(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        # Check if pre-delete is allowed
        if not self.delete_flag:
            msg = 'Pre-Delete skipped: Deletion of existing objects in the Tink platform is disabled.'
            logging.info(msg)
            result_log += os.linesep + msg
            return result_log
        else:
            msg = 'Pre-Delete enabled: Existing objects in the Tink platform will be deleted.'
            logging.info(msg)
            result_log += os.linesep + msg
            return result_log

        # Get user data
        users = self.dao.read_users()

        # Delete existing users
        result_log += self.authorize_client_delete(scope='user:delete', delete_dict=None)
        for e in users:
            delete_dict = {'external_user_id': e['external_user_id']}
            # Delete the user
            result_log += self.authorize_client_delete(scope='user:delete', delete_dict=delete_dict)

        result_log += request.to_string_formatted() + os.linesep*2 + response.to_string_formatted()
        return result_log

    """Initiates the ingestion of accounts in the Tink platform."""
    def ingest_accounts(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

    """Initiates the deletion of accounts in the Tink platform."""
    def delete_accounts(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

    """Initiates the retrieval of a list of all accounts in the Tink platform."""
    def list_accounts(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

    """Initiates the ingestion of transactions in the Tink platform."""
    def ingest_trx(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

    """Initiates the deletion of transactions in the Tink platform."""
    def delete_trx(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

    """Initiates the retrieval of a list of all transactions in the Tink platform."""
    def list_trx(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

    """Process the full PoC pileline.#
    Create users
    Ingest accounts
    Ingest transactions
    """
    def process(self):
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)


    def get_categories(self):#
        # Log current method running
        result_log = '+++ {c}.{m} +++\n'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name)
        logging.debug(result_log)

        service = api.CategoryService()
        return service.list_categories()


"""Selection of Tink scopes

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
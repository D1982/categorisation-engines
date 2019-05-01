import Categorisation.Tink.api as api
import Categorisation.Common.secret as sec

import logging
import os

class TinkModel:

    INSTANCE = None

    @staticmethod
    def get_instance():
        logging.info("Initiated:" + "TinkModel.get_instance()")

        """ Static access method. """
        if TinkModel.INSTANCE is None:
            TinkModel()
        return TinkModel.INSTANCE

    def __init__(self):
        """ Virtually private constructor. """
        if TinkModel.INSTANCE is not None:
            raise Exception("This class is a singleton!")
        else:
            TinkModel.INSTANCE = self


    def test_connectivity(self):
        s = api.MonitoringService()
        result1 = s.service_url('ping')+'=> {result}'.format(result=s.ping())
        result2 = s.service_url('healthy') + '=> {result}'.format(result=s.health_check())

        return result1 + os.linesep + result2

    def authentication(self):
        service = api.OAuthService()
        (response_msg, access_token, token_type, expires_in, scope) =\
            service.authorize_client_access(sec.TINK_CLIENT_ID, sec.TINK_CLIENT_SECRET)

        result = dict()

        result["message"] = response_msg
        result["access_token"] = access_token
        result["token_type"] = token_type
        result["expires_in"] = expires_in
        result["scope"] = scope

        return result


    def get_categories(self):
        service = api.CategoryService()
        return service.list_categories()

    def create_user(self, user_id):
        pass

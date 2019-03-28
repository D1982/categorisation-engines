""" Castlight Financial API usage PoC
Basic PoC for the interaction with the transaction categorisation engine of the UK vendor Castlight Financial (https://castlightfinancial.com)
Currently supporting their API in version 1 and version 2.

LINKS:
Logging HOWTO: https://docs.python.org/2/howto/logging.html
Castlight Developer Portal: https://develop.castlightfinancial.com
Creating a hypermedia-driven RESTful web service: https://openliberty.io/guides/rest-hateoas.html
Python DOCS (HTTPSConnection.set_tunnel): https://docs.python.org/3.4/library/http.client.html

"""
import Categorisation.Common.config as cfg
import Categorisation.Common.util as util
import Categorisation.Common.exceptions as ex

import http.client
import json
import logging
import os.path
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from enum import Enum


class API:
    def __init__(self):
        self.config = dict()

    def connect(self, use_proxy=False):
        try:
            # Establish HTTPSConnection
            if not use_proxy:
                conn = http.client.HTTPSConnection(cfg.API_URL_CASTLIGHT)
            else:
                logging.info("Establishing a HTTPSConnection with proxy server "+cfg.PROXY_URL+":"+str(cfg.PROXY_PORT))
                conn = http.client.HTTPSConnection(cfg.PROXY_URL, cfg.PROXY_PORT, timeout=cfg.TIMEOUT)
                logging.info("Tunneling to API endpoint " + cfg.API_URL_CASTLIGHT)
                conn.set_tunnel(cfg.API_URL_CASTLIGHT)

            if conn == None:
                raise ConnectionError
            else:
                return conn

        except Exception as e:
            errmsg = "Error:{0}".format(e.args or "")
            logging.info(errmsg)
            print(errmsg)
            quit()
            
            
class SupportedAPIs(Enum):
    CastlightAPIv1 = 'CastlightAPIv1'
    CastlightAPIv2 = 'CastlightAPIv2'


class APIConfig:
    def __init__(self):
        self.api_headers = dict()


class APIFactory:
    @staticmethod
    def create_api(api_version=SupportedAPIs.CastlightAPIv1):
        api = None
        logging.info("Initiated:" + "APIFactory.create_api()")

        if api_version == SupportedAPIs.CastlightAPIv1:
            logging.info(SupportedAPIs.CastlightAPIv1.value)
            api = CastlightAPIv1()
        elif api_version == SupportedAPIs.CastlightAPIv2:
            logging.info(SupportedAPIs.CastlightAPIv1.value)
            api = CastlightAPIv2()

        return api


class CastlightAPIConfig(APIConfig):

    def __init__(self):
        super().__init__()
        self.api_headers['Ocp-Apim-Subscription-Key'] = '8d2b8e00bc794f7c81fcdcc7359bb995'


class CastlightAPI:
    def __init__(self):
        self.config = CastlightAPIConfig()
        # self.headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': '8d2b8e00bc794f7c81fcdcc7359bb995'}
        self.headers = {'Content-Type': 'application/json'}
        self.headers['Ocp-Apim-Subscription-Key'] = self.config.api_headers['Ocp-Apim-Subscription-Key']
        logging.debug("Ocp-Apim-Subscription-Key: " + self.headers['Ocp-Apim-Subscription-Key'])
        self.params = urllib.parse.urlencode({})


    def connect(self, use_proxy=False):
        try:
            # Establish HTTPSConnection
            if not use_proxy:
                conn = http.client.HTTPSConnection(cfg.API_URL_CASTLIGHT)
            else:
                logging.info("Establishing a HTTPSConnection with proxy server "+cfg.PROXY_URL+":"+str(cfg.PROXY_PORT))
                conn = http.client.HTTPSConnection(cfg.PROXY_URL, cfg.PROXY_PORT, timeout=cfg.TIMEOUT)
                logging.info("Tunneling to API endpoint " + cfg.API_URL_CASTLIGHT)
                conn.set_tunnel(cfg.API_URL_CASTLIGHT)

            if conn == None:
                raise ConnectionError
            else:
                return conn

        except Exception as e:
            errmsg = "Error:{0}".format(e.args or "")
            logging.info(errmsg)
            print(errmsg)
            quit()


    def log_input_data(self, json_data, transactions=None):
        logging.debug("JSON: " + json.dumps(json_data, sort_keys=False, indent=4))
        logging.debug("TRANSACTIONS: ")
        for trx in transactions:
            rec = ''
            for i, fname in enumerate(self.fieldnames_request):
                rec = rec + str(trx[fname])
                if i < len(self.fieldnames_request)-1: # Skip delimiter for last element
                    rec = rec + cfg.CSV_DELIMITER
            logging.info(rec)


    def get_result_data(self, transactions, response_dict):
        pass


class CastlightAPIv1(CastlightAPI):
    def __init__(self):
        CastlightAPI.__init__(self)
        self.fieldnames_request = ("type", "description", "amount")
        self.fieldnames_response = ("categorisation_method", "category", "low_confidence", "probability", "subcategory")


    def log_input_data(self, json_data, transactions=None):
        CastlightAPI.log_input_data(self, json_data, transactions)


    def categorise_transactions(self, json_string):
        response_dict = {}
        request = "/caas/classify?{p}".format(p=self.params)
        logging.info(str(__class__.__name__) + "." + sys._getframe().f_code.co_name + ".VAR:request = " + request)

        try:
            conn = self.connect(use_proxy=cfg.USE_PROXY)

            # Fire Request
            logging.info("Firing the Request...")
            conn.request("POST", request, json_string, self.headers)
            # Get Response
            logging.info("Getting the Response...")
            response = conn.getresponse()
            # Convert bytes to string type
            response_str = response.read().decode('utf-8')
            response_status = response.status
            response_reason = response.reason
            conn.close()
            if response_str:
                return response_str
            else:
                return "Not received any response => {s}, {r}".format(s=response_status, r=response_reason)
        except Exception as e:
            errmsg = "Error:{0}".format(e.args or "")
            logging.info(errmsg)
            print(errmsg)
            quit()


    def get_result_data(self, transactions, response_dict):
        len1=len(transactions)
        len2=len(response_dict["classifications"])

        if len1 != len2:
            raise ex.ResponseMissingEntries(
                "Number of elements in request {p1} and response {p1} do not equal".format(p1=len1, p2=len2))


        result_list = transactions
        result_row = None

        # Append all the information from the response to the result_dict already containing the input
        if "classifications" in response_dict:
            for i, input_row in enumerate(result_list):
                for field in self.fieldnames_response:
                    if field in response_dict["classifications"][i]:
                        result_list[i][field] =  response_dict["classifications"][i][field]
        return result_list

class CastlightAPIv2(CastlightAPI):
    def __init__(self):
        CastlightAPI.__init__(self)
        self.fieldnames_request = ("transaction_id", "customer_id", "transaction_date", "type", "description", "amount")
        self.fieldnames_response = ("transaction_id", "customer_id", "transaction_date", "type", "description", "Amount", "label", "Confidence_random_forest", "category_random_forest", "subcategory_random_forest", "CR_version", "model_version")


    def log_input_data(self, json_data, transactions=None):
        CastlightAPI.log_input_data(self, json_data, transactions)


    def categorise_transactions(self, json_string):
        response_dict = {}
        operation_id = ''
        request = "/categorisation/transactions?{p}".format(p=self.params)
        logging.info(str(__class__.__name__) + "." + sys._getframe().f_code.co_name + ".VAR:request = " + request)

        try:
            conn = self.connect(use_proxy=cfg.USE_PROXY)
            conn.request("POST", request, json_string, self.headers)
            response = conn.getresponse()
            status = response.status
            reason = response.reason
            # Use this for API calls e.g. to get status of TRX processing and to get the categories back
            location = response.getheader("Location")
            operation_id = location.rsplit('/',1)[1]
            logging.info("OPERATION_ID: " + operation_id)
            print("OPERATION_ID: " + operation_id)
            conn.close()
            return (status, reason, operation_id)
        except Exception as e:
            errmsg = "Error:{0}".format(e.args or "")
            logging.info(errmsg)
            print(errmsg)
            return (500, errmsg, operation_id)


    def get_categorisation_status(self, operation_id):
        """
        So it turns out that the status update service is turned off in development at the moment.
        The system still works but the service that updates the file isn’t on!
        You will see ‘Not Started’ but its actually complete.
        We’re making some updates to how it works so it will be this way until Tuesday
        (but you can easily ignore it)
        """
        pass


    def get_categorised_transactions(self, operation_id):
        response_dict = {}
        headers = self.headers
        headers["Accept"] = 'application/json'
        request = "/categorisation/categorised_transactions/{operation_id}".format(operation_id=operation_id)
        logging.info(str(__class__.__name__) + "." + sys._getframe().f_code.co_name + ".VAR:request = " + request)

        try:
            conn = self.connect(use_proxy=cfg.USE_PROXY)
            conn.request("GET", request, None, headers)
            response = conn.getresponse()
            status = response.status
            reason = response.reason
            # Convert bytes to string type
            response_str = response.read().decode('utf-8')
            conn.close()
            return (status, reason, response_str)
        except Exception as e:
            errmsg = "Error:{0}".format(e.args or "")
            logging.info(errmsg)
            print(errmsg)


            return (status, reason, errmsg)

    def get_result_data(self, transactions, response_dict):
        result_list = list()
        if "classifications" in response_dict:
            for i, input_row in enumerate(response_dict["classifications"]):
                result_list.append(dict())
                for field in self.fieldnames_response:
                    if field in response_dict["classifications"][i]:
                        result_list[i][field] =  response_dict["classifications"][i][field]
        return result_list


class Castlight:

    def __init__(self, api_version=SupportedAPIs.CastlightAPIv1, test_mode=True):
        # Initiate Logger
        logging.basicConfig(filename='castlight.log', level=logging.DEBUG)
        logging.info('Program started.')
        self.api_version = api_version
        self.test_mode = test_mode
        self.api = APIFactory.create_api(api_version)
        logging.debug(type(self.api))
        self.file_handler = util.FileHandler()


    def read_transactions(self, input_filename):
        input_data = dict()
        transactions = []

        extension = os.path.splitext(input_filename)[1]
        if extension == '.csv' or extension == '.txt':
            input_data = self.file_handler.read_csv_file(input_filename, self.api.fieldnames_request)
        elif extension == '.json':
            input_data = self.file_handler.read_json_file(input_filename)

        return input_data


    def process_data(self, input_filename, output_filename):
        data = dict()
        transactions = list()
        categories = dict()
        result_data = dict()

        # --- Read input transactions from file
        transactions =  self.read_transactions(input_filename)
        data["transactions"] = transactions

        # Log what we are going to send
        self.api.log_input_data(data, transactions)

        # If the programm is running in test mode stop here
        if self.test_mode == True:
            msg = "Program runs in test mode. No API calls to be performed. Program stopped."
            logging.warning(msg)
            raise ex.TestModeWarning(msg)

        # --- Categorise Transactions using API version 1
        if self.api_version == SupportedAPIs.CastlightAPIv1:
            response_str = self.api.categorise_transactions(json.dumps(data))
            logging.info("RESPONSE: " + response_str)
            categories = json.loads(response_str)
            logging.debug("RESPONSE-JSON: " + json.dumps(categories, sort_keys=False, indent=4))
            if "time_taken" in categories:
                time_taken = categories["time_taken"]
                logging.info("TIME-TAKEN: " + str(time_taken))

                try:
                    result_data = self.api.get_result_data(transactions, categories)
                except ex.ResponseMissingEntries as e:
                    logging.error("EXCEPTION: " + e.text)

        # --- Categorise Transactions using API version 2
        if self.api_version == SupportedAPIs.CastlightAPIv2:

            # 1. Categorise Transactions (Start Job on Server)
            (status_post, msg_post, operation_id) = self.api.categorise_transactions(json.dumps(data))
            logging.info("RESPONSE: " + str(status_post) + msg_post + '{' + operation_id + '}')
            if status_post == 201: # Created
                # 2. Get Categorised Transactions
                while True:
                    msg = "Waiting " + str(cfg.TIMEOUT) + " seconds for categorisation job on server to be finished ..."
                    logging.info(msg)
                    print(msg)
                    time.sleep(cfg.TIMEOUT)
                    (status_get, msg_get, response_str) = self.api.get_categorised_transactions(operation_id)
                    logging.info(response_str)

                    if status_get == 200: # OK
                        logging.info("STATUS-GET: " + str(status_get))
                        logging.debug("RESPONSE-JSON: " + json.dumps(response_str, sort_keys=False, indent=4))
                        categorised_transactions = json.loads(response_str)
                        try:
                            result_data = self.api.get_result_data(transactions, categorised_transactions)
                        except ex.ResponseMissingEntries as e:
                            logging.error("EXCEPTION: " + e.text)
                        msg = "Categorisation Job on server finished successfully."
                        logging.info(msg)
                        print(msg)
                        break
                    else:
                        logging.error("GET Categorised Transactions failed: " + str(status_get) + " - " + str(msg_get))
            else:
                logging.error("Categorise Transactions (POST) failed: " + status_post + " - " + msg_post)
        # --- Write the output file
        if result_data:
            self.file_handler.write_csv_file(result_data, self.api.fieldnames_request + self.api.fieldnames_response, output_filename)


def user_input():

    print ("USER INPUT")
    print ("-----------------------------------")
    input_api_version = input("API Version [1|2]: ")
    if input_api_version == "1":
        api_version = SupportedAPIs.CastlightAPIv1
    elif input_api_version == "2":
        api_version = SupportedAPIs.CastlightAPIv2
    else:
        print("No valid input. Program stopped.")
        quit()  # quit at this point
    input_api_call = input("Do HTTP Request [y|n]")
    if input_api_call == "y":
        test_mode = False
    elif input_api_call == "n":
        test_mode = True
    else:
        print("No valid input. Program stopped.")
        quit()  # quit at this point
    print ("-----------------------------------")
    return (api_version, test_mode)


def main():
    # Get user input
    (api_version, test_mode) = user_input()

    myCastlight = Castlight(api_version, test_mode=test_mode)

    if myCastlight.api_version == SupportedAPIs.CastlightAPIv1:
        file_in = "csv/APIv1_Request.csv"
        file_out = "csv/APIv1_Response.csv"
    elif myCastlight.api_version == SupportedAPIs.CastlightAPIv2:
        file_in = "csv/APIv2_Request_N26.csv"
        file_out = "csv/APIv2_Response_N26.csv"

        logging.info("FILE-IN: " + file_in)
        logging.info("FILE-OUT: " + file_out)

    try:
        myCastlight.process_data(file_in, file_out)
        print("Data processed successfully")
    except ex.TestModeWarning as t:
        msg = "Warning: " + t.text
        logging.warning(msg)
        print(msg)
        quit(0) # quit at this point
    except Exception as e:
        errmsg = "Error:{0}".format(e.args or "")
        logging.error(errmsg)
        print("Error: " + errmsg)


if __name__ == '__main__':
    main()

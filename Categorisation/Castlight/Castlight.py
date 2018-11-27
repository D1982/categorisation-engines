"""
Links:
https://develop.castlightfinancial.com
https://openliberty.io/guides/rest-hateoas.html
https://realpython.com/python-json/
"""
from enum import Enum
import csv
import http.client
import json
import os.path
import urllib.error
import urllib.parse
import urllib.request

# Required for json output
# import pandas as pd
# import ast

CSV_DELIMITER = ',' # Standard Delimiter
URL = "gateway.castlightfinancial.com"
API_VERSION_1 = 'APIv1'
API_VERSION_2 = 'APIv2'

class ResponseMissingEntries(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class Castlight:

    def __init__(self, api_version=API_VERSION_1, api_call=False):
        # Parameters
        self.api_version = api_version
        self.api_call = api_call
        # HTTP Headers
        self.headers = {'Content-Type': 'application/json', 'Ocp-Apim-Subscription-Key': '8d2b8e00bc794f7c81fcdcc7359bb995'}
        # HTTP URL Parameters
        self.params = urllib.parse.urlencode({})
        # HTTP Request
        if api_version == API_VERSION_1:
            self.request = "/caas/classify?{p}".format(p=self.params)
        elif api_version == API_VERSION_2:
            self.request = "/categorisation/transactions?{p}".format(p=self.params)
        # Fieldnames depending on API Version (Required for CSV DictReader + DictWriter)
        if self.api_version == API_VERSION_1:
            self.fieldnames_request = ("type", "description", "amount")
            self.fieldnames_response = ("categorisation_method", "category", "low_confidence", "probability", "subcategory")
        elif self.api_version == API_VERSION_2:
            self.fieldnames_request = ("transaction_id", "customer_id", "transaction_date", "type", "description", "amount")
            # self.fieldnames_response = ("categorisation_method", "category", "low_confidence", "probability", "subcategory")


    def read_json_file(self, filename):
        extension = os.path.splitext(filename)[1]
        if extension == '.json':
            with open(filename) as json_data:
                json_dict = json.load(json_data)
        return json_dict


    def write_json_file(self, json_data, filename):
        jsonfile = open(filename, 'w')
        json.dump(json_data, jsonfile)
        jsonfile.write('\n')


    def read_csv_file(self, filename, skip_header=True):
        extension = os.path.splitext(filename)[1]
        if extension == '.csv' or extension == '.txt':
            csvfile = open(filename,'r')
            csvreader = csv.DictReader(csvfile, self.fieldnames_request)
            csv_data = []
            if skip_header == True:
                next(csvreader) # This skips the first row of the CSV file
            for row in csvreader:
                csv_data.append(row)
        return csv_data


    def write_csv_file(self, data, fieldnames, filename):
        csvfile = open(filename, 'w')
        csvwriter = csv.DictWriter(csvfile, fieldnames)
        csvwriter.writeheader()
        for rec in data:
            csvwriter.writerow(rec)


    def print_request_data(self, headers, request, json_data, transactions):
        print("REQUEST-HEADERS: ", headers)
        print("REQUEST-URL: ", request)
        print("\nREQUEST-BODY: ", json.dumps(json_data, sort_keys=False, indent=4))
        print("\nINPUT-TRANSACTIONS: ")
        for trx in transactions:
            rec = ''
            for i, fname in enumerate(self.fieldnames_request):
                rec = rec + str(trx[fname])
                if i < len(self.fieldnames_request)-1: # Skip delimiter for last element
                    rec = rec + CSV_DELIMITER
            print(rec)


    def call_api(self, request, json_string, headers):
        response_dict = {}

        try:
            conn = http.client.HTTPSConnection(URL)
            conn.request("POST", request, json_string, headers)
            response = conn.getresponse()
            # Convert bytes to string type
            response_str = response.read().decode('utf-8')
            response_error = response.reason, response.status
            # Use this for API calls e.g. to get status of TRX processing and to get the categories back
            operation_id = response.getheader("Location")
            print("RESPONSE-OPERATION_ID; ", operation_id)
            conn.close()
            if response_str:
                return response_str
            else:
                return "Not received any response => {e}".format(e=response_error)


        except Exception as e:
            errmsg = "\n[Errno {0}] {1}".format(e.errno, e.strerror)
            print(errmsg)
            return errmsg


    def merge_result_data(self, transactions, response_dict):
        len1=len(transactions)
        len2=len(response_dict["classifications"])

        if self.api_version == API_VERSION_1 and len1 != len2:
            raise ResponseMissingEntries(
                "Number of elements in request {p1} and response {p1} do not equal".format(p1=len1, p2=len2))

        result_list = transactions
        result_row = None
        for i, input_row in enumerate(result_list):

            if self.api_version == API_VERSION_1:
                result_list[i]["categorisation_method"] = response_dict["classifications"][i]["categorisation_method"]
                result_list[i]["category"] = response_dict["classifications"][i]["category"]
                result_list[i]["low_confidence"] = response_dict["classifications"][i]["low_confidence"]
                result_list[i]["probability"] = response_dict["classifications"][i]["probability"]
                result_list[i]["subcategory"] = response_dict["classifications"][i]["subcategory"]
            elif self.api_version == API_VERSION_2:
                pass
        return result_list


    def trx_classification(self, request_filename, response_filename):
        json_data = dict()

        extension = os.path.splitext(request_filename)[1]
        if extension == '.csv' or extension == '.txt':
            transactions = self.read_csv_file(request_filename)
            json_data["transactions"] = transactions
        elif extension == '.json':
            json_data = self.read_json_file(request_filename)
        self.print_request_data(self.headers, self.request, json_data, transactions)
        if self.api_call == False:
            print("\nACTION: No request fired!")
            pass
        else:
            response_str = self.call_api(self.request, json.dumps(json_data), self.headers)
            response_dict = dict()

            if response_str:
                print("\nRESPONSE: ", response_str)
                response_dict = json.loads(response_str)

            if response_dict:
                time_taken = response_dict["time_taken"]
                print("TIME-TAKEN: ", time_taken)
                print("\nRESPONSE-JSON: ", json.dumps(response_dict, sort_keys=False, indent=4))

                try:
                    result_data = {}
                    result_data = self.merge_result_data(transactions, response_dict)
                except ResponseMissingEntries as e:
                    print("\nEXCEPTION: ".format(e.super().message))

                # Write the output file
                if result_data:
                    self.write_csv_file(result_data, self.fieldnames_request + self.fieldnames_response, response_filename)


def user_input():

    print ("USER INPUT")
    print ("-----------------------------------")
    input_api_version = input("API Version [1|2]: ")
    if input_api_version == "1":
        api_version = API_VERSION_1
    elif input_api_version == "2":
        api_version = API_VERSION_2
    else:
        print("No valid input. Program stopped.")
        quit()  # quit at this point
    input_api_call = input("Do HTTP Request [y|n]")
    if input_api_call == "y":
        api_call = True
    elif input_api_call == "n":
        api_call = False
    else:
        print("No valid input. Program stopped.")
        quit()  # quit at this point
    print ("-----------------------------------")
    return (api_version, api_call)


def main():
    # Get user input
    (api_version, api_call) = user_input()

    myCastlight = Castlight(api_version, api_call=api_call)
    # myCastlight = Castlight(API_VERSION_1, api_call=True)

    if myCastlight.api_version == API_VERSION_1:
        file_in = "request_v1.csv"
        file_out = "response_v1.csv"
    elif myCastlight.api_version == API_VERSION_2:
        file_in = "request_v2.csv"
        file_out = "response_v2.csv"

    print("API-VERSION:", myCastlight.api_version)
    print("API-CALL:", str(myCastlight.api_call))
    print("FILE-IN:", file_in)
    print("FILE-OUT:", file_out)

    myCastlight.trx_classification(file_in, file_out)


if __name__ == '__main__':
    main()
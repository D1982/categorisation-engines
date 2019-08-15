"""Common configuration items."""

import logging

from enum import Enum


# Enumerations

class MessageDetailLevel(Enum):
    """
    Enumeration of different message detail levels.

    This values are being used in different areas of the code in order to
    steer the way text output is being composed.
    """
    Low = 'Low message detail restricted to the minimum'
    Medium = 'Medium message detail including important additional information'
    High = 'High message detail including some debugging information'


class HTTPStatusCode(Enum):
    """
    Enumeration of different http status code groups
    """
    Code2xx = '2xx = Codes between >= 200 and <= 299'
    Code4xx = '4xx = Codes between >= 400 and <= 499'
    Code5xx = '5xx = Codes between >= 500 and <= 599'


class EntityType(Enum):
    """
    Enumeration of valid entity types relevant for the application.
    These can be used to transfer the appropriate data over the DAO.

    """
    User = 'Tink User Entity'
    Account = 'Tink Account Entity'
    Transaction = 'Tink Transaction Entity'
    Log = 'The applciation logs'


class InputSourceType(Enum):
    """
    Enumeration of valid input source types.
    These can be used to define kind of input data for the DAO.
    """
    File = 'Flat File Input (CSV)'
    Database = 'Database Input'
    JSON = 'JSON File Input'


# Constants
SUPPORTED_FILE_TYPES =  [('Text files', '*.txt'), ('CSV files', '*.csv')]

CSV_DELIMITER = ';'  # Default delimiter for csv file processing

USE_PROXY = False  # Default setting for http proxy usage

PROXY_URL = '11.112.142.4'  # Default URL of the http proxy

PROXY_PORT = '8080'  # Default port of the http proxy

TIMEOUT = 5  # Default timeout for http calls

API_URL_CASTLIGHT = 'gateway.castlightfinancial.com'  # Castlight API endpoint URL

API_URL_TINK = 'https://api.tink.se'  # Tink enterprise API endpoint URL

API_URL_TINK_CONNECTOR = 'https://api.tink.com/connector'  # Tink connector API endpoint URL

API_CALL_DELAY_IN_SECS = 2  # Minimum delay between dependent API calls in seconds

IN_FILE_PATTERN_TINK = 'data/Tink*_In.csv'  # Default file pattern for input files of the Tink PoC

OUT_FILE_PATTERN_TINK = 'data/Tink*_Out.csv'  # Default file pattern for output files of the Tink PoC

TINK_LOGFILE = 'logs/tink.log'  # Default name of the Tink processing log file

UI_STRING_MAX_WITH = 150  # Default value for the with of the output text in the ui

LOG_LEVEL = logging.DEBUG  # Default log level for logging

UI_RESULT_LOG_MSG_DETAIL = MessageDetailLevel.Low


class TinkConfig:
    """
    Configuration class that can be used over the whole application.
    Settings will be driven by instances of class TinkUI.

    This is a Singleton!


    The following properties are being administrated:
    _delete_flag
        True: All data with the given keys will be deleted before it is ingested again
        into the Tink platform
        False: Data will be ingested without deleting potentially existing data within
        the Tink platform. If data does already exist then appropriate calls might
        result in conflicts
    """
    __instance = None  # Instance will be stored here

    @staticmethod
    def get_instance():
        """
        Static access method.
        """
        if TinkConfig.__instance is None:
            TinkConfig()

        instance: TinkConfig = TinkConfig.__instance

        return instance

    def __init__(self):
        """
        Virtually private constructor.
        """
        if TinkConfig.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TinkConfig.__instance = self

            self._delete_flag: bool = False
            self._message_detail_level: MessageDetailLevel = UI_RESULT_LOG_MSG_DETAIL
            self._result_file_flag: bool = False
            self._proxy_flag: bool = USE_PROXY
            self._log_level: int = LOG_LEVEL
            self._user_source = 'unbound'
            self._acc_source = 'unbound'
            self._trx_source = 'unbound'

    @property
    def delete_flag(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._delete_flag

    @delete_flag.setter
    def delete_flag(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._delete_flag = value

    @property
    def message_detail_level(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._message_detail_level

    @message_detail_level.setter
    def message_detail_level(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        for e in MessageDetailLevel:
            if value == e:
                self._message_detail_level = e

    @property
    def result_file_flag(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._result_file_flag

    @result_file_flag.setter
    def result_file_flag(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._result_file_flag = value

    @property
    def proxy_flag(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return _self._proxy_flag

    @proxy_flag.setter
    def proxy_flag(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._proxy_flag = value
        
    @property
    def log_level(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._log_level

    @log_level.setter
    def log_level(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._log_level = value
        
    @property
    def user_source(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._user_source

    @user_source.setter
    def user_source(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._user_source = value

    @property
    def account_source(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._account_source

    @account_source.setter
    def account_source(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._account_source = value

    @property
    def transaction_source(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._transaction_source

    @transaction_source.setter
    def transaction_source(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._transaction_source = value

    @property
    def user_target(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._user_target

    @user_target.setter
    def user_target(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._user_target = value

    @property
    def account_target(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._account_target

    @account_target.setter
    def account_target(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._account_target = value

    @property
    def transaction_target(self):
        """
        Get the current value of the corresponding property _<method_name>.
        :return: The current value of the corresponding property _<method_name>.
        """
        return self._transaction_target

    @transaction_target.setter
    def transaction_target(self, value):
        """
        Set the current value of the corresponding property _<method_name>.
        :param value: The new value of the corresponding property _<method_name>.
        """
        self._transaction_target = value

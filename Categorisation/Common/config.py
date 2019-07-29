"""Common configuration items."""

import logging

from enum import Enum


# Enumerations

class TinkEntityType(Enum):  # TODO: This class is to be decommissioned
    """
    Enumeration of entity type that can be a source of data.
    """
    UserEntity = 'UserEntity'
    AccountEntity = 'AccountEntity'
    TransactionEntity = 'TransactionEntity'


class DataSourceType(Enum):  # TODO: This class is to be decommissioned
    """
    Enumeration of different types of data sources.
    """
    CSVFileSource = 'CSVFileSource'
    TinkUI = 'TinkUI'


class MessageDetailLevel(Enum):
    """
    Enumeration of different message detail levels.

    This values are being used in different areas of the code in order to
    steer the way text output is being composed.
    """
    Low = 'Low message detail restricted to the minimum'
    Medium = 'Medium message detail including important additional information'
    High = 'High message detail including some debugging information'


class HTTPStatusCode(Enum):  # TODO: This class is to be decommissioned
    """
    Enumeration of different http status code groups
    """
    Code2xx = '2xx = Codes between >= 200 and <= 299'
    Code4xx = '4xx = Codes between >= 400 and <= 499'
    Code5xx = '5xx = Codes between >= 500 and <= 599'


# Constants

CSV_DELIMITER = ';'  # Default delimiter for csv file processing

USE_PROXY = False  # Default setting for http proxy usage

PROXY_URL = '11.112.142.4'  # Default URL of the http proxy

PROXY_PORT = '8080'  # Default port of the http proxy

TIMEOUT = 5  # Default timeout for http calls

API_URL_CASTLIGHT = 'gateway.castlightfinancial.com'  # Castlight API endpoint URL

API_URL_TINK = 'https://api.tink.se'  # Tink enterprise API endpoint URL

API_URL_TINK_CONNECTOR = 'https://api.tink.com/connector'  # Tink connector API endpoint URL

IN_FILE_PATTERN_TINK = 'data/TinkReq*.csv'  # Default file pattern for input files of the Tink PoC

OUT_FILE_PATTERN_TINK = 'data/TinkResp*.csv'  # Default file pattern for output files of the Tink PoC

TINK_LOGFILE = 'logs/tink.log'  # Default name of the Tink processing log file

UI_STRING_MAX_WITH = 200  # Default value for the with of the output text in the ui

LOG_LEVEL = logging.DEBUG  # Default log level for logging

UI_RESULT_LOG_MSG_DETAIL = MessageDetailLevel.Low

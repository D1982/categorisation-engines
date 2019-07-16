"""Common configuration items."""

from enum import Enum

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

"""Enumeration of entity type that can be a source of data."""


class TinkEntityType(Enum):  # TODO: This class is to be decommissioned
    UserEntity = 'UserEntity'
    AccountEntity = 'AccountEntity'
    TransactionEntity = 'TransactionEntity'


"""Enumeration of different types of data sources."""


class DataSourceType(Enum):  # TODO: This class is to be decommissioned
    CSVFileSource = 'CSVFileSource'
    TinkUI = 'TinkUI'

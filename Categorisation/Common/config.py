""" Configuration items

"""

from enum import Enum

# File processing
CSV_DELIMITER = ';' # Standard Delimiter

# Proxy settings
USE_PROXY = False

PROXY_URL = '11.112.142.4'

PROXY_PORT = '8080'

# HTTP settings
TIMEOUT = 5

# Castlight specifics
API_URL_CASTLIGHT = 'gateway.castlightfinancial.com'

# Tink specifics
TINK_LOGFILE = 'tink.log'

API_URL_TINK = 'https://api.tink.se'

IN_FILE_PATTERN_TINK = 'data/TinkReq*.csv'

OUT_FILE_PATTERN_TINK = 'data/TinkResp*.csv'

# UI
UI_STRING_MAX_WITH = 100

# Enumerations
class TinkEntityType(Enum):
    UserEntity = 'UserEntity'
    AccountEntity = 'AccountEntity'
    TransactionEntity = 'TransactionEntity'


class DataSourceType(Enum):
    CSVFileSource = 'CSVFileSource'
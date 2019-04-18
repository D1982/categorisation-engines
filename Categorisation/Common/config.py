""" Configuration items

"""
from enum import Enum

# File settings
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
IN_FILE_PATTERN_TINK = 'data/TinkRequest_*.csv'
OUT_FILE_PATTERN_TINK = 'data/TinkResponse_*.csv'

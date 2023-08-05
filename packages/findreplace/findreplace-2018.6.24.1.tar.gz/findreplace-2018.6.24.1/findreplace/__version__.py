from datetime import datetime

CURRENT_DATE = datetime.now()

YEAR = CURRENT_DATE.year
MONTH = CURRENT_DATE.month
DAY = CURRENT_DATE.day
SUB_VERSION = 1

VERSION = (YEAR, MONTH, DAY, SUB_VERSION)

__version__ = '.'.join(map(str, VERSION))
from datetime import datetime

# CURRENT_DATE = datetime.now()

# YEAR = CURRENT_DATE.year()
# MONTH = CURRENT_DATE.month()
# DAY = CURRENT_DATE.day()
# SUB_VERSION = 0

VERSION = (2018, 6, 17, 0)

# VERSION = (YEAR, MONTH, DAY, SUB_VERSION)

__version__ = '.'.join(map(str, VERSION))

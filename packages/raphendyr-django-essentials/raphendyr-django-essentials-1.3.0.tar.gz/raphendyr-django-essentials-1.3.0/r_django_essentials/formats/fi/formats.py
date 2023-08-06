# This file is distributed under the same license as the Django package.
#
# The *_FORMAT strings use the Django date format syntax,
# see http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = 'j. E Y'                      # 25, Lokakuu 2006
TIME_FORMAT = 'G.i'                         # 14.30
DATETIME_FORMAT = r'j. E Y \k\e\l\l\o G.i'  # 25, Lokakuu 2006 kello 14.40
YEAR_MONTH_FORMAT = 'F Y'                   # October 2006
MONTH_DAY_FORMAT = 'j. F'                   # 25. 2006
SHORT_DATE_FORMAT = 'j.n.Y'                 # 25.5.2006
SHORT_DATETIME_FORMAT = 'j.n.Y G.i'         # 25.5.2006 14.30
FIRST_DAY_OF_WEEK = 1  # Monday

from ..en.formats import (
    DATE_INPUT_FORMATS, DATETIME_INPUT_FORMATS, TIME_INPUT_FORMATS,
    DECIMAL_SEPARATOR, THOUSAND_SEPARATOR, NUMBER_GROUPING,
)

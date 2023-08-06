# This file is distributed under the same license as the Django package.
#
# The *_FORMAT strings use the Django date format syntax,
# see http://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
DATE_FORMAT = 'N j, Y'              # Oct 25, 2006
TIME_FORMAT = 'P'                   # 2 p.m.
DATETIME_FORMAT = 'N j, Y, P'       # Oct 25, 2006, 2 p.m.
YEAR_MONTH_FORMAT = 'F Y'           # October 2006
MONTH_DAY_FORMAT = 'F j'            # October 25
SHORT_DATE_FORMAT = 'Y-m-d'         # 2006-10-25         us: 'm/d/Y'
SHORT_DATETIME_FORMAT = 'Y-m-d G:i' # 2006-10-25 14:30   us: 'm/d/Y P'
FIRST_DAY_OF_WEEK = 1  # Monday

# The *_INPUT_FORMATS strings use the Python strftime format syntax,
# see http://docs.python.org/library/datetime.html#strftime-strptime-behavior
# Kept ISO formats as they are in first position
DATE_INPUT_FORMATS = [
    '%Y-%m-%d',                 # '2006-10-25'
    '%m/%d/%Y', '%m/%d/%y',     # '10/25/2006', '10/25/06'
    '%d.%m.%Y', '%d.%m.%y',     # '20.3.2014', '20.3.14'
    # '%b %d %Y', '%b %d, %Y',  # 'Oct 25 2006', 'Oct 25, 2006'
    # '%d %b %Y', '%d %b, %Y',  # '25 Oct 2006', '25 Oct, 2006'
    # '%B %d %Y', '%B %d, %Y',  # 'October 25 2006', 'October 25, 2006'
    # '%d %B %Y', '%d %B, %Y',  # '25 October 2006', '25 October, 2006'
]
DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'

    '%d.%m.%Y %H.%M.%S',     # '20.3.2014 14.30.59'
    '%d.%m.%Y %H.%M.%S.%f',  # '20.3.2014 14.30.59.000200'
    '%d.%m.%Y %H.%M',        # '20.3.2014 14.30'
    '%d.%m.%Y',              # '20.3.2014'
    '%d.%m.%y %H.%M.%S',     # '20.3.14 14.30.59'
    '%d.%m.%y %H.%M.%S.%f',  # '20.3.14 14.30.59.000200'
    '%d.%m.%y %H.%M',        # '20.3.14 14.30'
    '%d.%m.%y',              # '20.3.14'

    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    '%m/%d/%y',              # '10/25/06'
]
TIME_INPUT_FORMATS = [
    '%H:%M:%S',     # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M',        # '14:30'

    '%H.%M.%S',     # '14.30.59'
    '%H.%M.%S.%f',  # '14.30.59.000200'
    '%H.%M',        # '14.30'
]

DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = '\xa0'  # Non-breaking space
NUMBER_GROUPING = 3

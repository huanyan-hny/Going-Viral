import datetime
import logging
from datetime import timedelta
import os, errno

logger = logging.getLogger('django')


def check_int(string):
    return string.isdigit()


def try_parse_float(string):
    try:
        flt = float(string)
        return flt
    except ValueError:
        return False


def try_parse_date(string):
    if check_int(string) is False:
        print 'Error: ', string, ' is not a timestamp'
        return None
    date = datetime.datetime.fromtimestamp(float(string))
    if date.year < 2016:
        print 'Error: the date converted from ', string, ' must be wrong'
        return None
    return date


def offset_date(the_date):
    start = datetime.date(2016, 11, 27)
    return abs((the_date - start).days)


def generate_date_from_offset(offset):
    start = datetime.date(2016, 11, 27)
    return start + timedelta(days=offset)


def try_read_date(string):
    logger.info('Read date ' + string)
    # input validation
    result = string.split('/', 2)
    if len(result) < 2:
        return False
    elif result[2] < 2016:
        return False

    # parse date
    the_date = datetime.date(int(result[2]), int(result[0]), int(result[1]))
    return the_date


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def safe_open_w(path):
    ''' Open "path" for writing, creating any parent directories as needed.
    '''
    mkdir_p(os.path.dirname(path))
    return open(path, 'w')

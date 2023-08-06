import time
from datetime import datetime


class DTFormat(object):
    date_format = None
    datetime_format = None

    def __init__(self, date_format='%Y-%m-%d', datetime_format='%Y-%m-%d %H:%M:%S'):
        self.date_format = date_format
        self.datetime_format = datetime_format


class DateTimeUtils():
    @staticmethod
    def to_time_stamp(datetime_str):
        '''
        2018-01-01 00:00:00 -->  1514736000

        :param datetime_str: datetime string
        :returns: unix time stamp
        :raises ValueError: datetime string format error
        '''
        try:
            dtf = DTFormat()
            struct_time = time.strptime(datetime_str, dtf.datetime_format)
            return time.mktime(struct_time)
        except ValueError as e:
            return None

    @staticmethod
    def now():
        '''
        get now datetime

        :returns: datetime string
        '''
        dft = DTFormat()
        return datetime.now().strftime(dft.datetime_format)

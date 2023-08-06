# -*- coding: utf-8 -*-

import logging
import datetime
import calendar
import re


# 连接超时，单位秒
connect_timeout = 30

connect_pool_size = 10

_ISO8601_RE = re.compile(
    r'(?P<year>\d+)-(?P<month>01|02|03|04|05|06|07|08|09|10|11|12)-(?P<day>0[1-9]|([1-2]\d)|(3[0-1]))T(?P<hour>([0-1]\d)|(2[0-3])):(?P<minute>[0-5]\d):(?P<second>[0-5]\d)\.\d\d\dZ$'
)


logger = logging.getLogger()


def get_value(value, default_value):
    if value is None:
        return default_value

    return value


def get_logger():
    return logger


def iso8601_to_unixtime(time_string):
    """把ISO8601时间字符串（形如，2012-02-24T06:07:48.000Z）转换为UNIX时间，精确到秒。"""

    m = _ISO8601_RE.match(time_string)

    if not m:
        raise ValueError(time_string + " is not in valid ISO8601 format")

    day = int(m.group('day'))
    month = int(m.group('month'))
    year = int(m.group('year'))
    hour = int(m.group('hour'))
    minute = int(m.group('minute'))
    second = int(m.group('second'))

    tm = datetime.datetime(year, month, day, hour, minute, second).timetuple()

    return calendar.timegm(tm)


class SimplifiedBucketInfo(object):
    """:func:`list_buckets <oss2.Service.list_objects>` 结果中的单个元素类型。"""
    def __init__(self, name, creation_date):
        #: Bucket名
        self.name = name

        #: Bucket的创建时间，类型为int。参考 :ref:`unix_time`。
        self.creation_date = creation_date


class SimplifiedObjectInfo(object):
    #def __init__(self, key, last_modified, etag, type, size, storage_class):
    def __init__(self, key, last_modified, etag, size, storage_class):
        #: 文件名，或公共前缀名。
        self.key = key

        #: 文件的最后修改时间
        self.last_modified = last_modified

        #: HTTP ETag
        self.etag = etag

        #: 文件类型
        # self.type = type

        #: 文件大小
        self.size = size

        #: 文件的存储类别，是一个字符串。
        self.storage_class = storage_class

    def is_prefix(self):
        """如果是公共前缀，返回True；是文件，则返回False"""
        return self.last_modified is None


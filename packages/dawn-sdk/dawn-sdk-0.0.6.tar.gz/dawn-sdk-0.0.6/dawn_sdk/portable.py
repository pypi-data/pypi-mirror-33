# -*- coding: utf-8 -*-

"""
兼容python2/python3
"""

import sys

python2 = (sys.version_info[0] == 2)
python3 = (sys.version_info[0] == 3)

try:
    import simplejson as json
except (ImportError, SyntaxError):
    import json

if python2:
    from urllib import quote as urlquote, unquote as urlunquote
    from urlparse import urlparse

    def utf8_string(data):
        """若输入为unicode， 则转为utf-8编码的bytes；其他则原样返回。"""
        if isinstance(data, unicode):
            return data.encode('utf-8')
        else:
            return data

    def to_bytes(data):
        return utf8_string(data)

    def to_string(data):
        """把输入转换为str对象"""
        return to_bytes(data)

    def unicode_string(data):
        """把输入转换为unicode，要求输入是unicode或者utf-8编码的bytes。"""
        if isinstance(data, bytes):
            return data.decode('utf-8')
        else:
            return data


elif python3:
    from urllib.parse import quote as urlquote, unquote as urlunquote
    from urllib.parse import urlparse

    def utf8_string(data):
        """若输入为str（即unicode），则转为utf-8编码的bytes；其他则原样返回"""
        if isinstance(data, str):
            return data.encode(encoding='utf-8')
        else:
            return data

    def unicode_string(data):
        """把输入转换为unicode，要求输入是unicode或者utf-8编码的bytes。"""
        if isinstance(data, bytes):
            return data.decode('utf-8')
        else:
            return data
      
    def to_bytes(data):
        return utf8_string(data)

    def to_string(data):
        """若输入为bytes，则认为是utf-8编码，并返回str"""
        return unicode_string(data)


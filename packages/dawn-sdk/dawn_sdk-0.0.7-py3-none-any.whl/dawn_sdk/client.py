# -*- coding: utf-8 -*-

import os
import requests
from requests.structures import CaseInsensitiveDict

from . import common
from .portable import utf8_string
from .error import RequestError
from .progress import LimitedReader, file_object_left_bytes
from .mime import mime_type


_CHUNK_SIZE = 8 * 1024
  

class Session(object):
    def __init__(self):
        self.session = requests.Session()

        pool_size = common.connect_pool_size
        self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=pool_size, pool_maxsize=pool_size))

    def do_request(self, req, timeout):
        try:
            return Response(self.session.request(
                req.method,
                req.url,
                data=req.data,
                params=req.params,
                headers=req.headers,
                stream=True,
                timeout=timeout))
        except requests.RequestException as e:
            raise RequestError(e)


class Request(object):
    def __init__(self, method, url, data=None, params=None, headers=None):
        self.method = method
        self.url = url
        self.data = _to_http_body(data)
        self.params = params or {}

        if not isinstance(headers, CaseInsensitiveDict):
            self.headers = CaseInsensitiveDict(headers)
        else:
            self.headers = headers

        # ...
        if 'Accept-Encoding' not in self.headers:
            self.headers['Accept-Encoding'] = None


class Response(object):
    def __init__(self, response):
        self.response = response
        self.status = response.status_code
        self.headers = response.headers

        # When a response contains no body, iter_content() cannot
        # be run twice (requests.exceptions.StreamConsumedError will be raised).
        # For details of the issue, please see issue #82
        #
        # To work around this issue, we simply return b'' when everything has been read.
        #
        # Note you cannot use self.response.raw.read() to implement self.read(), because
        # raw.read() does not uncompress response body when the encoding is gzip etc., and
        # we try to avoid depends on details of self.response.raw.
        self.__all_read = False
      
    def read(self, amt=None):
        if self.__all_read:
            return b''
        
        if amt is None:
            content_list = []
            for chunk in self.response.iter_content(_CHUNK_SIZE):
                content_list.append(chunk)
            content = b''.join(content_list)
        
            self.__all_read = True
            return content
        
        try:
            return next(self.response.iter_content(amt))
        except StopIteration:
            self.__all_read = True
            return b''
    
    def __iter__(self):
        return self.response.iter_content(_CHUNK_SIZE)


def _to_http_body(data):
    data = utf8_string(data)

    if hasattr(data, '__len__'):
        return data
    
    if hasattr(data, 'seek') and hasattr(data, 'tell'):
        return LimitedReader(data, file_object_left_bytes(data))
    
    return data


def set_content_type(headers, name):
    """根据文件名在headers里设置Content-Type。如果headers中已经存在Content-Type，则直接返回。"""
    headers = headers or {}

    if 'Content-Type' in headers:
        return headers

    ext = os.path.splitext(name)
    ext_name = 'default'
    if len(ext) == 2:
        ext_name = ext[1][1:]

    content_type = mime_type(ext_name)
    if content_type:
        headers['Content-Type'] = content_type

    return headers


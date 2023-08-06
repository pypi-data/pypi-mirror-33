# -*- coding: utf8 -*-

import re
import xml.etree.ElementTree as ElementTree
from xml.parsers import expat

from .portable import to_string


STATUS_ClIENT_ERROR = -1
STATUS_REQUEST_ERROR = -2


class BaseError(Exception):
    def __init__(self, status, headers, body, detail):
        # HTTP的状态码
        self.status = status
        # 请求id，用于跟踪一个请求。
        self.request_id = headers.get('x-amz-request-id', '')
        # HTTP响应体
        self.body = body
        # 详细的错误信息，通常是一个xml，但是经过解析后，被存在一个dict内。
        self.detail = detail

        # 错误信息中的错误码
        self.code = self.detail.get('Code', '')
        # 错误信息中的错误消息
        self.message = self.detail.get('Message', '')

    def __str__(self):
        error = {'HTTP-Code': self.status, 'request-id': self.request_id, 'detail': self.detail}
        return str(error)

    def _str_with_body(self):
        error = {'HTTP-Code': self.status, 'request-id': self.request_id, 'detail': self.body}
        return str(error)


class ClientError(BaseError):
    def __init__(self, message):
        BaseError.__init__(self, STATUS_CLIENT_ERROR, {}, 'ClientError: ' + message, {})
    
    def __str__(self):
        return self._str_with_body()
  

class RequestError(BaseError):
    def __init__(self, e):
        BaseError.__init__(self, STATUS_REQUEST_ERROR, {}, 'RequestError: ' + str(e), {})
        self.exception = e

    def __str__(self):
        return self._str_with_body()


class HTTPError(BaseError):
    pass


class NotFound(HTTPError):
    status = 404
    code = ''


class InvalidRequest(HTTPError):
    status = 400
    code = 'InvalidRequest'


class OperationNotSupported(HTTPError):
    status = 400
    code = 'OperationNotSupported'


class InvalidArgument(HTTPError):
    status = 400
    code = 'InvalidArgument'

    def __init__(self, status, headers, body, detail):
        super(InvalidArgument, self).__init__(status, headers, body, detail)
        self.name = detail.get('ArgumentName')
        self.value = detail.get('ArgumentValue')


class InvalidObjectName(HTTPError):
    status = 400
    code = 'InvalidObjectName'


class NoSuchBucket(NotFound):
    status = 404
    code = 'NoSuchBucket'


class NoSuchKey(NotFound):
    status = 404
    code = 'NoSuchKey'


class NoSuchUpload(NotFound):
    status = 404
    code = 'NoSuchUpload'


class AccessDenied(HTTPError):
    status = 403
    code = 'AccessDenied'


class SignatureDoesNotMatch(HTTPError):
    status = 403
    code = 'SignatureDoesNotMatch'


# 动态的获取子类和孙子类
def _iter_subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        for sub_sub in _iter_subclasses(sub):
            yield sub_sub


def _parse_xml_body(body):
    try:
        root = ElementTree.fromstring(body)
        if root.tag != 'Error':
            return {}

        detail = {}
        for child in root:
            detail[child.tag] = child.text
        return detail
    except ElementTreeParseError:
        return _guess_xml_detail(body)


def _guess_xml_detail(body):
    detail = {}
    body = to_string(body)

    if '<Error>' not in body or '</Error>' not in body:
        return detail
    
    m = re.search('<Code>(.*)</Code>', body)
    if m:
        detail['Code'] = m.group(1)

    m = re.search('<Message>(.*)</Message>', body)
    if m:
        detail['Message'] = m.group(1)
    
    return detail


def make_response_error(resp):
    status = resp.status
    headers = resp.headers
    body = resp.read(4096)
    detail = _parse_xml_body(body)
    code = detail.get('Code', '')

    try:
        error = _STATUS_TO_ERROR_DICT[(status, code)]
        return error(status, headers, body, detail)
    except KeyError:
        return HTTPError(status, headers, body, detail)


# 生成 (status, code): 
_STATUS_TO_ERROR_DICT = {}
for cls in _iter_subclasses(HTTPError):
    status = getattr(cls, 'status', None)
    code = getattr(cls, 'code', None)

    if status is not None and code is not None:
        _STATUS_TO_ERROR_DICT[(status, code)] = cls

# XML parsing exceptions have changed in Python2.7 and ElementTree 1.3
if hasattr(ElementTree, 'ParseError'):
    ElementTreeParseError = (ElementTree.ParseError, expat.ExpatError)
else:
    ElementTreeParseError = (expat.ExpatError)


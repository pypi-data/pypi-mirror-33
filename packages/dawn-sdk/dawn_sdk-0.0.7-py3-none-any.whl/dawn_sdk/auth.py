# -*- coding: utf-8 -*-

import hmac
import base64
import time
from hashlib import sha1 as sha
from email.utils import formatdate

from .url import _to_quoted_string as to_quoted_string
from .portable import utf8_string, to_string, urlquote
from .common import get_logger


class Authorize(object):
    """用于保存用户的access_key/secret_key, 以及计算签名。"""
    def __init__(self, access_key, secret_key):
        self.access_key = access_key.strip()
        self.secret_key = secret_key.strip()

    def _sign_url(self, req, bucket, key, expires):
        future = int(time.time()) + expires

        req.headers['date'] = str(future)
        signature = self.__make_signature(req, bucket, key)

        req.params['AWSAccessKeyId'] = self.access_key
        req.params['Expires'] = str(future)
        req.params['Signature'] = signature

        return req.url + '?' + '&'.join(to_quoted_string(k, v) for k, v in req.params.items())

    def _sign_request(self, req, bucket, key):
        if 'date' not in req.headers and 'x-amz-date' not in req.headers:
            req.headers['date'] = formatdate(
              timeval=None,
              localtime=False,
              usegmt=True)

        signature = self.__make_signature(req, bucket, key)
        get_logger().debug('signature={0}'.format(signature))

        req.headers['Authorization'] = "AWS {0}:{1}".format(self.access_key, signature)    
        get_logger().debug('header[Authorization]={0}'.format(req.headers['Authorization']))

    def __make_signature(self, req, bucket, key):
        sign_string = self.__get_sign_string(req, bucket, key)

        key = utf8_string(self.secret_key)
        msg = utf8_string(sign_string)
          
        get_logger().debug('string to sign:\n{0}'.format(sign_string))

        h = hmac.new(key, msg, digestmod=sha)
        
        get_logger().debug('HMAC digest={0}'.format(h.digest()))
        return to_string(base64.b64encode(h.digest())).strip()
    
    def __get_sign_string(self, req, bucket, key):

        content_md5 = req.headers.get('content-md5', '')
        content_type = req.headers.get('content-type', '')
        date = ''
        if 'x-amz-date' not in req.headers:
            date = req.headers.get('date', '')

        canon_headers = self.__get_canon_headers(req)
        canon_resource = self.__get_canon_resource(req, bucket, key)

        return '\n'.join([req.method, content_md5, content_type, date, canon_headers + canon_resource])
    
    def __get_canon_headers(self, req):
        headers = req.headers
        canon_headers = []
        #todo: 头中相同的域需要合并。
        for k, v in headers.items():
            lk = k.lower()
            if lk.startswith('x-amz-'):
                canon_headers.append((lk, v))

        canon_headers.sort(key=lambda x: x[0])
        if canon_headers:
            return '\n'.join(k + ':' + v for k, v in canon_headers) + '\n'

        return ''

    def __get_canon_resource(self, req, bucket, key):
        if not bucket:
            return '/'
        key = utf8_string(key)
        key = urlquote(key, '/')
        return '/{0}/{1}{2}'.format(bucket, key, self.__get_subresource(req.params))

    _subresource_keys = frozenset(
        [
            'acl', 'location', 'logging', 'partNumber', 'policy', 'requestPayment',
            'torrent', 'versioning', 'versionId', 'website', 'uploads', 'uploadId',
            'response-content-type', 'response-content-language', 'response-expires',
            'response-cache-control', 'delete', 'lifecycle', 'response-content-disposition',
            'response-content-encoding', 'tagging', 'notification', 'cors'
        ]
    )
    
    def __get_subresource(self, params):
        if not params:
            return ''
        
        subresource = []
        for k, v in params.items():
            if k in self._subresource_keys:
                subresource.append((k, v))
        
        subresource.sort(key=lambda k: k[0])

        if subresource:
            return '?' + '&'.join(self.__query_string(k, v) for k, v in subresource)
        
        return ''
    
    def __query_string(self, key, value):
        if value:
            return key + '=' + value
        
        return key


# -*- coding: utf8 -*-

from .misc import *


class Result(object):
    def __init__(self, resp):
        self.resp = resp
        self.status = resp.status
        self.headers = resp.headers
        self.request_id = resp.headers.get('x-amz-request-id', '')

  
# etag value is '"etag"' so need strip the `"`.
def _get_etag(headers):
    return misc._get_dict_value(headers, 'etag', lambda x: x.strip('"'))


class PutObject(Result):
    def __init__(self, resp):
        super(PutObject, self).__init__(resp)

        self.etag = _get_etag(self.headers)


class InitMultipartUpload(Result):
    def __init__(self, resp):
        super(InitMultipartUpload, self).__init__(resp)

        self.upload_id = None


# 列出bucket下面的所有对象。
class ListObjects(Result):
    def __init__(self, resp):
        super(ListObjects, self).__init__(resp)
    
        self.is_continous = False
        self.next_marker = ''
        self.objects = []
        self.prefixs = []
  

class ListBuckets(Result):
    def __init__(self, resp):
        super(ListBuckets, self).__init__(resp)
        self.is_continuous = False
        self.next_marker = ''
        self.buckets = []


class ListMultipartUploads(Result):
    def __init__(self, resp):
        super(ListMultipartUploads, self).__init__(resp)
        self.is_continous = False
        self.next_key_marker = ''
        self.next_upload_id_marker = ''
        self.uploads = []
        self.prefixs = []


class ListParts(Result):
    def __init__(self, resp):
        super(ListParts, self).__init__(resp)

        self.is_continous = False
        self.next_marker = ''
        self.parts = []


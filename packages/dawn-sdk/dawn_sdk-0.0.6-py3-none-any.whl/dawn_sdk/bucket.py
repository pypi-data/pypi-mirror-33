# -*- coding: utf8 -*-

import time

from . import client
from . import error
from . import misc
from . import progress
from . import url
from . import xml_body
from . import limited
from .common import get_value, connect_timeout, get_logger
from .portable import to_string, unicode_string
from .result import PutObject, InitMultipartUpload, ListBuckets, ListObjects


def _normalize_endpoint(endpoint):
    if endpoint.startswith('http://') or endpoint.startswith('https://'):
        return endpoint
    return 'http://' + endpoint


class _Base(object):
    def __init__(self, auth, endpoint, is_cname, session, conn_timeout):
        self.auth = auth
        self.endpoint = _normalize_endpoint(endpoint.strip())
        self.session = session or client.Session()
        self.timeout = get_value(conn_timeout, connect_timeout)
        
        self._url_make = url._Maker(self.endpoint, is_cname)

    def _do(self, method, bucket, key, **kwargs):
        key = to_string(key)
        req = client.Request(method, self._url_make(bucket, key), **kwargs)

        get_logger().debug("Bucket Request url={0}".format(req.url))

        self.auth._sign_request(req, bucket, key)

        resp = self.session.do_request(req, timeout=self.timeout)
        if resp.status // 100 != 2:
            raise error.make_response_error(resp)

        content_length = misc._get_dict_value(resp.headers, 'content-length', int)
        if content_length is not None and content_length == 0:
            resp.read()
        
        return resp

    def _parse_result(self, resp, parse_func, cls):
        result = cls(resp)
        parse_func(result, resp.read())
        return result


class Service(_Base):
    """用于Service操作的类，如罗列用户所有的Bucket。

    用法 ::

      >>> import oss2
      >>> auth = oss2.Auth('your-access-key-id', 'your-access-key-secret')
      >>> service = oss2.Service(auth, 'oss-cn-hangzhou.aliyuncs.com')
      >>> service.list_buckets()
      <oss2.models.ListBucketsResult object at 0x0299FAB0>

    :param auth: 包含了用户认证信息的Auth对象
    :type auth: oss2.Auth

    :param str endpoint: 访问域名，如杭州区域的域名为oss-cn-hangzhou.aliyuncs.com

    :param session: 会话。如果是None表示新开会话，非None则复用传入的会话
    :type session: oss2.Session

    :param float connect_timeout: 连接超时时间，以秒为单位。
    :param str app_name: 应用名。该参数不为空，则在User Agent中加入其值。
        注意到，最终这个字符串是要作为HTTP Header的值传输的，所以必须要遵循HTTP标准。
    """
    def __init__(self, auth, endpoint, session=None, connect_timeout=None):
        super(Service, self).__init__(auth, endpoint, False, session, connect_timeout)

    def list_buckets(self, prefix='', marker='', max_keys=100):
        """根据前缀罗列用户的Bucket。
    
        :param str prefix: 只罗列Bucket名为该前缀的Bucket，空串表示罗列所有的Bucket
        :param str marker: 分页标志。首次调用传空串，后续使用返回值中的next_marker
        :param int max_keys: 每次调用最多返回的Bucket数目
    
        :return: 罗列的结果
        :rtype: oss2.models.ListBucketsResult
        """
        resp = self._do('GET', '', '',
                        params={'prefix': prefix,
                                'marker': marker,
                                'max-keys': str(max_keys)})
        return self._parse_result(resp, xml_body.parse_list_buckets, ListBuckets)


class Bucket(_Base):
    """用于Bucket和Object操作的类，诸如创建、删除Bucket，上传、下载Object等。

    用法 ::

      >>> import dawn
      >>> auth = dawn.Authorize('your-access-key-id', 'your-access-key-secret')
      >>> bucket = dawn.Bucket(auth, 'http://<domain>', 'your-bucket')
      >>> bucket.put_object('readme.txt', 'content of the object')
        <dawn.result.PutObject object at 0x029B9930>

    :param auth: 包含了用户认证信息的Authorize对象
    :type auth: dawn.Authorize

    :param str endpoint: 访问域名或者CNAME
    :param str bucket: Bucket名
    :param bool is_cname: 如果endpoint是CNAME则设为True；反之，则为False。

    :param session: 会话。如果是None表示新开会话，非None则复用传入的会话
    :type session: dawn.http.Session

    :param float connect_timeout: 连接超时时间，以秒为单位。
    """
    def __init__(self, auth, endpoint, bucket, is_cname=False, session=None, connect_timeout=None):
        super(Bucket, self).__init__(auth, endpoint, is_cname, session, connect_timeout)

        self.bucket = bucket.strip()

    def sign_url(self, key, expires, method='GET', headers=None, params=None):
        """生成签名URL。

        常见的用法是生成加签的URL以供授信用户下载，如为log.jpg生成一个5分钟后过期的下载链接::

          >>> bucket.sign_url('GET', 'log.jpg', 5 * 60)
          'http://<oss-domain>/<bucket>/logo.jpg?OSSAccessKeyId=YourAccessKeyId\&Expires=1447178011&Signature=UJfeJgvcypWq6Q%2Bm3IJcSHbvSak%3D'

        :param key: 文件名
        :param expires: 过期时间（单位：秒），链接在当前时间再过expires秒后过期
        :param method: HTTP方法，如'GET'、'PUT'、'DELETE'等, 默认为GET
        :type method: str

        :param headers: 需要签名的HTTP头部，如名称以x-amz-meta-开头的头部（作为用户自定义元数据）、
          Content-Type头部等。对于下载，不需要填。
        :type headers: 可以是dict，建议是http.CaseInsensitiveDict

        :param params: 需要签名的HTTP查询参数

        :return: 签名URL。
        """
        key = to_string(key)
        req = client.Request(method, self._url_make(self.bucket, key), headers=headers, params=params)

        return self.auth._sign_url(req, self.bucket, key, expires)

    def put_object(self, key, data, headers=None, progress_callback=None, upload_speed_limited=None):
        headers = client.set_content_type(client.CaseInsensitiveDict(headers), key)

        dlen = progress._get_data_length(data)
        chunk_size = progress._CHUNK_SIZE
        if upload_speed_limited:
            data = limited.DelayReader(data, upload_speed_limited)
            chunk_size = data.chunk_size
            get_logger().info('uplpad speed limit(bytes/s)={0}, chunk={1}'.format(upload_speed_limited, chunk_size))
            print('uplpad speed limit(bytes/s)={0}, chunk={1}'.format(upload_speed_limited, chunk_size))

        if progress_callback:
            data = progress.make_progress_adapter(data, progress_callback, chunk_size, dlen)

        begin = time.time()
        resp = self.__do_object('PUT', key, data=data, headers=headers)
        end = time.time()
        get_logger().info('put object speed(bytes/s)={0}'.format(int(dlen / (end - begin))))
        print('put object speed(bytes/s)={0}'.format(int(dlen / (end - begin))))
        return PutObject(resp)

    def put_object_from_file(self, key, filename, headers=None, progress_callback=None, upload_speed_limited=None):
        headers = client.set_content_type(client.CaseInsensitiveDict(headers), filename)

        with open(unicode_string(filename), 'rb') as f:
            return self.put_object(key, f, headers=headers, progress_callback=progress_callback, upload_speed_limited=upload_speed_limited)


    def init_multipart_upload(self, key, headers=None):
        """初始化分片上传。

        返回值中的 `upload_id` 以及Bucket名和Object名三元组唯一对应了此次分片上传事件。

        :param str key: 待上传的文件名

        :param headers: HTTP头部
        :type headers: 可以是dict，建议是http.CaseInsensitiveDict

        :return: :class:`InitMultipartUpload<dawn.result.InitMultipartUpload>`
        """
        headers = client.set_content_type(client.CaseInsensitiveDict(headers), key)

        resp = self.__do_object('POST', key, params={'uploads': ''}, headers=headers)

        parser = xml_body.Parser(resp)
        
        return parser.init_multipart_upload()

    def upload_part(self, key, upload_id, part_number, data, progress_callback=None, upload_speed_limited=None, headers=None):
        """上传一个分片。

        :param str key: 待上传文件名，这个文件名要和 :func:`init_multipart_upload` 的文件名一致。
        :param str upload_id: 分片上传ID
        :param int part_number: 分片号，最小值是1.
        :param data: 待上传数据。
        :param progress_callback: 用户指定进度回调函数。可以用来实现进度条等功能。参考 :ref:`progress_callback` 。

        :param headers: 用户指定的HTTP头部。可以指定Content-MD5头部等
        :type headers: 可以是dict，建议是http.CaseInsensitiveDict

        :return: :class:`PutObject <dawn.result.PutObject>`
        """
        dlen = progress._get_data_length(data)
        chunk_size = progress._CHUNK_SIZE
        if upload_speed_limited:
            data = limited.DelayReader(data, upload_speed_limited)
            chunk_size = data.chunk_size
            get_logger().info('uplpad speed limit(bytes/s)={0}, chunk={1}'.format(upload_speed_limited, chunk_size))
            print('uplpad speed limit(bytes/s)={0}, chunk={1}'.format(upload_speed_limited, chunk_size))

        if progress_callback:
            data = progress.make_progress_adapter(data, progress_callback, chunk_size, dlen)

        begin = time.time()
        resp = self.__do_object('PUT', key,
                                params={'uploadId': upload_id, 'partNumber': str(part_number)},
                                headers=headers,
                                data=data)
        end = time.time()
        get_logger().info('upload multipart speed(bytes/s)={0}'.format(int(dlen / (end - begin))))
        print('upload multipart speed(bytes/s)={0}'.format(int(dlen / (end - begin))))
        return PutObject(resp)

    def complete_multipart_upload(self, key, upload_id, parts, headers=None):
        """完成分片上传，创建文件。

        :param str key: 待上传的文件名，这个文件名要和 :func:`init_multipart_upload` 的文件名一致。
        :param str upload_id: 分片上传ID

        :param parts: PartInfo列表。PartInfo中的part_number和etag是必填项。其中的etag可以从 :func:`upload_part` 的返回值中得到。
        :type parts: list of `PartInfo <dawn.xml_body.PartInfo>`

        :param headers: HTTP头部
        :type headers: 可以是dict，建议是http.CaseInsensitiveDict

        :return: :class:`PutObject <dawn.result.PutObject>`
        """
        maker = xml_body.Maker()

        data = maker.complete_upload_request(sorted(parts, key=lambda p: p.part_number))
        resp = self.__do_object('POST', key,
                                params={'uploadId': upload_id},
                                data=data,
                                headers=headers)

        return PutObject(resp)

    def abort_multipart_upload(self, key, upload_id):
        """取消分片上传。

        :param str key: 待上传的文件名，这个文件名要和 :func:`init_multipart_upload` 的文件名一致。
        :param str upload_id: 分片上传ID

        :return: :class:`Result <dawn.result.Result>`
        """
        resp = self.__do_object('DELETE', key,
                                params={'uploadId': upload_id})
        return Result(resp)

    def list_objects(self, prefix='', delimiter='', marker='', max_keys=100):
        """根据前缀罗列Bucket里的文件。
 
        :param str prefix: 只罗列文件名为该前缀的文件
        :param str delimiter: 分隔符。可以用来模拟目录
        :param str marker: 分页标志。首次调用传空串，后续使用返回值的next_marker
        :param int max_keys: 最多返回文件的个数，文件和目录的和不能超过该值
 
        :return: :class:`ListObjectsResult <oss2.models.ListObjectsResult>`
        """
        resp = self.__do_object('GET', '',
                                params={'prefix': prefix,
                                        'delimiter': delimiter,
                                        'marker': marker,
                                        'max-keys': str(max_keys),
                                        'encoding-type': 'url'})
        return self._parse_result(resp, xml_body.parse_list_objects, ListObjects)

    def __do_object(self, method, key, **kwargs):
        return self._do(method, self.bucket, key, **kwargs)

    def __do_bucket(self, method, **kwargs):
        return self._do(method, self.bucket_name, '', **kwargs)


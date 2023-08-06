# -*- coding: utf8 -*-


from .misc import is_ipaddr, is_localhost
from .portable import urlquote, urlparse


class _Maker(object):
    def __init__(self, endpoint, is_cname):
        p = urlparse(endpoint)

        self.scheme = p.scheme
        self.netloc = p.netloc
        self.is_cname = is_cname

    def __call__(self, bucket, key):
        key = urlquote(key, '/')

        # CNAME: 泛域名方式　http://<bucket>.<domain>/<key>
        if self.is_cname:
            return '{0}://{1}/{2}'.format(self.scheme, self.netloc, key)
        
        # ip格式或者localhost
        if is_ipaddr(self.netloc) or is_localhost(self.netloc):
            if bucket:
                return '{0}://{1}/{2}/{3}'.format(self.scheme, self.netloc, bucket, key)
            else:
                return '{0}://{1}/{2}'.format(self.scheme, self.netloc, key)

        # bucket和key都为空
        if not bucket:
            assert not key
            return '{0}://{1}'.format(self.scheme, self.netloc)

        # 我们自己的url http://<domain>/<bucket>/<key>
        return '{0}://{1}/{2}/{3}'.format(self.scheme, self.netloc, bucket, key)


def _to_quoted_string(k, v):
    if v:
        return urlquote(k, '') + '=' + urlquote(v, '')
    
    return urlquote(k, '')

# -*- coding: utf8 -*-


import os

from .error import ClientError
from .portable import to_bytes


_CHUNK_SIZE = 8 * 1024


class LimitedReader(object):
    """限制读， 可以限定读取的长度 """
    def __init__(self, file_object, size):
        self.file_object = file_object
        self.size = size
        self.offset = 0
    
    def read(self, size=None):
        if self.offset >= self.size:
            return ''
        
        if (size is None or size < 0) or (size + self.offset >= self.size):
            data = self.file_object.read(self.size - self.offset)
            self.offset = self.size
            return data
        
        self.offset += size
        return self.file_object.read(size)

    @property
    def len(self):
        return self.size


def file_object_left_bytes(file_object):
    now_pos = file_object.tell()

    file_object.seek(0, os.SEEK_END)
    end = file_object.tell()
    file_object.seek(now_pos, os.SEEK_SET)

    return end - now_pos


def _get_data_length(data):
    if hasattr(data, '__len__'):
        return len(data)
    
    if hasattr(data, 'len'):
        return data.len
    
    if hasattr(data, 'seek') and hasattr(data, 'tell'):
        return file_object_left_bytes(data)

    return None


def _invoke_progress(progress_callback, transfered_bytes, total_bytes):
    if progress_callback:
        progress_callback(transfered_bytes, total_bytes)


class _IterableAdapter(object):
    def __init__(self, data, progress_callback=None):
        self.iter = iter(data)
        self.progress = progress_callback
        self.offset = 0

    def __iter__(self):
        return self
      
    def __next__(self):
        return self.next()

    def next(self):
        _invoke_progress(self.progress, self.offset, None)

        content = next(self.iter)
        self.offset += len(content)

        return content


class _ReadableAdapter(object):
    def __init__(self, file_object, progress_callback=None, chunk_size=None):
        self.file_object = file_object
        self.progress = progress_callback
        self.chunk_size = chunk_size
        self.offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()
    
    def next(self):
        content = self.read(self.chunk_size)

        if content:
            return content

        return StopIteration

    def read(self, size=None):
        content = self.file_object.read(size)
        _invoke_progress(self.progress, self.offset, None)

        if content:
            self.offset += len(content)

        return content

  
class _BufferAdapter(object):
    def __init__(self, data, progress_callback=None, chunk_size=None, size=None):
        self.data = to_bytes(data)
        self.progress = progress_callback
        self.chunk_size = chunk_size
        self.size = size
        self.offset = 0

    @property
    def len(self):
        return self.size

    # for python 2.x
    def __bool__(self):
        return True
    # for python 3.x
    __nonzero__=__bool__

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        content = self.read(self.chunk_size)
        if content:
            return content
        
        return StopIteration

    def read(self, size=None):
        if self.offset >= self.size:
            return ''
        
        if size is None or size < 0:
            bytes_to_read = self.size - self.offset
        else:
            bytes_to_read = min(size, self.size - self.offset)
        
        if isinstance(self.data, bytes):
            content = self.data[self.offset:self.offset+bytes_to_read]
        else:
            content = self.data.read(bytes_to_read)
        
        self.offset += bytes_to_read
        _invoke_progress(self.progress, min(self.offset, self.size), self.size)

        return content


def make_progress_adapter(data, progress_callback, chunk_size, size=None):
    """返回一个适配器，从而在读取 `data` ，即调用read或者对其进行迭代的时候，能够
      调用进度回调函数。当 `size` 没有指定，且无法确定时，上传回调函数返回的总字节数为None。

    :param data: 可以是bytes、file object或iterable
    :param progress_callback: 进度回调函数，参见 :ref:`progress_callback`
    :param size: 指定 `data` 的大小，可选

    :return: 能够调用进度回调函数的适配器
    """
    data = to_bytes(data)

    if size is None:
        size = _get_data_length(data)

    if size is None:
        if hasattr(data, 'read'):
            return _ReadableAdapter(data, progress_callback, chunk_size)
        elif hasattr(data, '__iter__'):
            return _IterableAdapter(data, progress_callback)
        else:
            raise ClientError('{0} is not a file object, nor an iterator'.format(data.__class__.__name__))
    else:
        return _BufferAdapter(data, progress_callback, chunk_size, size)


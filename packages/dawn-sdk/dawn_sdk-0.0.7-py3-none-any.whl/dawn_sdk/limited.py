# -*- coding: utf8 -*-

import math
import time

from monotonic import monotonic

from .error import ClientError


class DelayReader(object):
    def __init__(self, data, bytes_per_second, times_per_second=20, sleep_func=time.sleep):
        self._data = data
        self._bytes_per_second = bytes_per_second
        self._times_per_second = times_per_second
        self._sleep = sleep_func
        self._per_elapsed = 1.0 / times_per_second
        if self._bytes_per_second < 1024:
          self._bytes_per_second = 1024
        self._chunk = self._bytes_per_second // times_per_second
        self._now = None
        self._next_time = None
        self._bucket = self._chunk
        #print(self._chunk)

    def __iter__(self):
        return self
    
    def __next__(self):
        return self.next()

    def next(self):
        content = self.read(self._chunk)

        if content:
            return content

        return StopIteration

    def _update_elapsed(self):
        now = monotonic()
        if now > self._next_time:
            elapsed = now - self._next_time
            ticks = int(math.ceil(elapsed / self._per_elapsed))
            self._bucket += ticks * self._chunk
            self._next_time += ticks * self._per_elapsed
    
    def _read(self, size=None):
        if hasattr(self._data, 'read'):
            return self._data.read(size)
        else:
            raise ClientError('{0} is not a file object, '.format(data.__class__.__name__))

    def read(self, size=None):
        if self._now is None:
            self._now = monotonic()
            self._next_time = self._now + self._per_elapsed
        
        if size is None:
            size = self._chunk

        self._update_elapsed()
        
        if size > self._bucket:
            now = monotonic()
            ticks = (size - self._bucket) / self._chunk
            time_df = self._next_time - now - self._per_elapsed
            delay = ticks * self._per_elapsed
            #print('ticks={0}, time_diff={1}, delay={2}'.format(ticks, time_df, delay))
            if time_df > 0:
                delay += time_df
            self._sleep(delay)
            self._update_elapsed()

        data = self._read(size)
        self._bucket -= size
        return data
    
    @property
    def chunk_size(self):
        return self._chunk


if __name__ == "__main__":
    with open('20m.vbox', 'rb') as f:
        dr = DelayReader(f, 1024000, 20)

        t_zero = time.time()
        while True:
            data = dr.read(2048000)
            print("Got %d at %0.2f" % (len(data),  time.time() - t_zero))
            if len(data) == 0:
                break
  

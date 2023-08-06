# -*- coding: utf8 -*-

# config reader


class Config(object):
    def __init__(self, conf_file='config.txt'):
        self._dict = {}
        with open(conf_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('//'):
                    p = line.split('=', 1)
                    if len(p) == 2:
                        self._dict[p[0]] = p[1]
    
    @property
    def dict(self):
        return self._dict
        

# -*- coding: utf8 -*-

import socket


_ALPHA_AND_DIGIT = 'abcdefghijklmnopqrstuvwxyz0123456789'
_CONNECTOR = '-'
_BUCKET_CHAR_SET = set(_ALPHA_AND_DIGIT + _CONNECTOR) 


def _get_dict_value(d, key, converter=lambda x: x):
    if key in d:
        return converter(d[key])
    return None


def is_ipaddr(netloc):
    loc = netloc.split(':')
    try:
        socket.inet_aton(str(loc))
    except socket.error:
        return False
    
    return True


def is_localhost(netloc):
    loc = netloc.split(':')[0]
    return loc == 'localhost'


def bucket_name_is_valid(name):
    if len(name) < 3 or len(name) > 63:
        return False

    if name[-1] == _CONNECTOR:
        return False
    
    if name[0] not in _ALPHA_AND_DIGIT:
        return False
    
    return set(name) <= _BUCKET_CHAR_SET


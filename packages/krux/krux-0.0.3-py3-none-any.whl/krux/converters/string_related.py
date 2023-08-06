# -*- coding:utf-8 -*-

import re

__all__ = ['str2list', 'dict2str']


def str2list(s, pattern=',|;|:|#|&|\||\s+'):
    l = re.split(pattern, s)
    if len(l) == 1 and l[0] == '':
        return []
    else:
        return l


def dict2str(d, fmt='{}={}', delimiter='&', sort=True):
    keys = sorted(d.keys()) if sort else d.keys()
    tokens = [fmt.format(k, d[k]) for k in keys]
    return delimiter.join(tokens)

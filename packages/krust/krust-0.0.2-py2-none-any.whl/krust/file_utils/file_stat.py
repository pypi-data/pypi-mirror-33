# -*- coding:utf-8 -*-

import six
import os


def filesize(f):
    """Return the size of f in bytes"""
    if isinstance(f, file):
        now_pos = f.tell()
        f.seek(0, 2)
        size = f.tell()
        f.seek(now_pos)
        return size
    else:
        return os.stat(f).st_size


def DU(path):
    pass
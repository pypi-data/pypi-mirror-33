# -*- coding:utf-8 -*-

import six
import os
import sys


__all__ = [
    'P',
    'PWD', 'DIRNAME', 'BASENAME', 'add_slash',
    'CD',
    'get_rel_path', 'find_link_orig',
    'get_ext', 'strip_ext', 'sub_ext'
]

def P(path):
    """expand ~ and $ in the path"""
    return os.path.expanduser(os.path.expandvars(path))


def PWD():
    return os.getcwdu()


def DIRNAME(fname=None, absolute=False):
    if fname is None:
        fname = sys.modules['__main__'].__dict__['__file__']
        return os.path.dirname(os.path.abspath(fname))
    else:
        if absolute:
            fname = os.path.abspath(fname)
        return os.path.dirname(fname)


BASENAME = os.path.basename


def add_slash(path):
    """Add a slash to the end of path if not exist."""
    return path.rstrip('/') + '/'


def CD(path=None):
    """CD changes dir
    """
    if path is None:
        path = P('~')
    else:
        path = P(path)
    if path == '':
        return
    return os.chdir(path)


def get_rel_path(path, base):
    """get relative path, e.g., get_rel_path('abc/de/fg', 'abc') => 'de/fg'
    """
    lb = len(base)
    assert path[:lb] == base
    if len(path) == lb:
        rel_path = ''
    elif path[lb] == '/':
        rel_path = path[lb+1:]
    else:
        rel_path = path[lb:]
    return rel_path


def find_link_orig(path, max_depth=99):
    """Try to find the orig of a link."""
    count = 0
    while count < max_depth:
        if os.path.islink(path):
            path = os.readlink(path)
        else:
            return path
        count += 1
    return path


def get_ext(path):
    """get .ext from a path"""
    return os.path.splitext(path)[1]


def strip_ext(path):
    """strips .ext from a path"""
    return os.path.splitext(path)[0]


def sub_ext(orig, new_ext):
    """sub .ext with a new one"""
    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext
    return strip_ext(orig) + new_ext


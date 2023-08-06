# -*- coding:utf-8 -*-

import six
import os
import re

import glob

__all__ = [
    'sorted_walk',
    'list_all_file',
    'LS', 'LS_R'
]


def sorted_walk(top, **kwarg):
    """returns the sorted result in a list consisting os.walk's 3-tuple: (dirpath, dirnames, filename).
    kwargs: os.path's kwargs, i.e. topdown=True[, onerror=None[, followlinks=False]]"""
    if 'followlinks' not in kwarg:
        kwarg['followlinks'] = True
    w = os.walk(top, **kwarg)
    res = list(w)
    res.sort()
    for stuff in res:
        stuff[1].sort()
        stuff[2].sort()
    return res


def list_all_file(top=None, fname_pattern=r'.*', dir_pattern=r'.*',
                  ignore_hidden=True, recursive=True, base_only=False, **kwarg):
    """returns a list of filenames that matches the 2 regex patterns,
    kwargs: os.path's kwargs, i.e. topdown=True[, onerror=None[, followlinks=True]]"""
    if top is None:
        top = '.'
        remove_dot_slash = True
    else:
        remove_dot_slash = False

    try:
        newtop = os.path.expanduser(os.path.expandvars(top))
    except Exception:
        newtop = top

    if newtop != '/' and newtop.endswith('/'):
        newtop = newtop[:-1]

    if not os.path.exists(newtop):
        return []
    if 'followlinks' not in kwarg:
        kwarg['followlinks'] = True
    if recursive:
        walktuplelist = sorted_walk(newtop, **kwarg)
    else:
        fnames = sorted(os.listdir(newtop))
        walktuplelist = [('', [], fnames)]
    filelist = []
    for walktuple in walktuplelist:
        d = walktuple[0]
        if remove_dot_slash and d.startswith('./'):
            d = d[2:]

        if re.search(dir_pattern, d):
            if ignore_hidden:
                sorted_dirs = sorted(d.split(os.path.sep))
                sorted_dirs = [subd for subd in sorted_dirs if subd not in ('', '.', '..')]
                if len(sorted_dirs) > 0 and sorted_dirs[0].startswith('.'):
                    continue
            for fname in walktuple[2]:
                if re.search(fname_pattern, fname):
                    if ignore_hidden:
                        if fname.startswith('.') or fname.endswith('~'):
                            continue
                    filelist.append(os.path.join(d, fname))
    if base_only:
        if not remove_dot_slash:
            trim_n = len(newtop) + 1
            filelist = [fn[trim_n:] for fn in filelist]
    return filelist


def LS(top=None, *args, **kwargs):
    """wrapping for list_all_file() with recursive default as False.
    kwargs are the same as list_all_file, i.e.,
        fname_pattern, dir_pattern, ignore_hidden, recursive, followlinks, etc.
    """
    recursive = kwargs.pop('recursive', False)
    return list_all_file(top, *args, recursive=recursive, **kwargs)


LS_R = list_all_file


# def LS_GREP(top=None, pattern=r'(.*)', fast=True):
#     try:
#         re_pattern = re.sub(r'\{([a-zA-Z_][^/:}]*)(:[^/}]*)*\}', r'(?P<\1>[^/]*)', pattern)
#         if re_pattern != pattern:
#             re_pattern = re.sub(r'\.', '\.', re_pattern)
#             re_pattern = '^' + re_pattern.lstrip('^')
#             re_pattern = re_pattern.rstrip('$') + '$'
#             pattern = re_pattern
#     except Exception as e:
#         warn(repr(e))
#
#     if fast:
#         glob_pattern = pattern.lstrip('^').rstrip('$')
#         glob_pattern = re.sub(r'(\.(\*|\+))', '*', glob_pattern)                     # '.*|+' -> '*'
#         glob_pattern = re.sub(r'(\[[^]]*\](\*|\+))', '*', glob_pattern)              # '[...]*|+' -> '*'
#         glob_pattern = re.sub(r'(\[[^]]*\])', '?', glob_pattern)                # '[...]' -> '?'
#         glob_pattern = re.sub(r'(\\[sSwWdD](\*|\+))', '*', glob_pattern)             # '\[sSwWdD]*|+' -> '*'
#         glob_pattern = re.sub(r'(\\[sSwWdD])', '*', glob_pattern)               # '\[sSwWdD]' -> '?'
#         glob_pattern = re.sub(r'(\\\.)', '.', glob_pattern)                     # '\.' -> '.'
#         glob_pattern = re.sub(r'(\([^)]*\))', '*', glob_pattern)                # '(...)' -> '*'
#         # TODO: more conversion rules
#         if top:
#             glob_pattern = os.path.join(top, glob_pattern)
#         all_fnames = glob(glob_pattern)
#     else:
#         all_fnames = LS_R(top)
#
#     return grep(pattern, all_fnames)
#
# def LS_GROUP(top=None, pattern=r'(.*)', fast=True, keys=None, exclude_keys=None):
#     grep_res = LS_GREP(top=top, pattern=pattern, fast=fast)
#
#     group_paras = {}
#     groups = {}
#     for fname, info in grep_res:
#         if keys:
#             d = {}
#             for k in keys:
#                 if k in info:
#                     d[k] = info[k]
#         else:
#             d = info.copy()
#
#         to_pop = set(exclude_keys) if exclude_keys else set()
#         for k in d:
#             if isinstance(k, int):
#                 to_pop.add(k)
#
#         for k in to_pop:
#             d.pop(k, None)
#
#         keystr = dict2str(d)
#         group_paras.setdefault(keystr, d)
#         fnames = groups.setdefault(keystr, [])
#         fnames.append(fname)
#
#     res = []
#     for keystr in sorted(groups.keys()):
#         res.append((groups[keystr], group_paras[keystr]))
#
#     return res


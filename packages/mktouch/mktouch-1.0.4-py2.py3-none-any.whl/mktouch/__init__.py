#!/usr/bin/env python
import os
from public import public


def _mkdir(path):
    dirname = os.path.dirname(path)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)


def _utime(path):
    try:
        os.utime(path, None)
    except Exception:
        open(path, 'a').close()


@public
def mktouch(path):
    if not path:
        return
    _mkdir(path)
    if not os.path.exists(path):
        open(path,"w").write("")
    else:
        _utime(path)

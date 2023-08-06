#!/usr/bin/env python
from public import public
import runcmd


@public
def get():
    return runcmd.run(["wallpaper"])._raise().out


@public
def set(path):
    return runcmd.run(["wallpaper", path])._raise()

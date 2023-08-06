#!/usr/bin/env python
import os
from public import public
import runcmd
import temp


def _flags(flags=None):
    if not flags:
        return []
    if isinstance(flags, list):
        return ["-s"] + flags
    return ["-s", flags]


@public
def run(applescript, flags=None):
    if os.path.exists(applescript):
        path = applescript
    else:
        path = temp.tempfile()
        open(path, "w").write(applescript)
    cmd = ["osascript", path] + _flags(flags)
    return runcmd.run(cmd)

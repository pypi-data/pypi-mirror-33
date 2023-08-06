#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cli_args
from public import public
import runcmd


@public
def notify(**kwargs):
    if "m" not in kwargs and "message" not in kwargs:
        kwargs["m"] = ""
    args = cli_args.make(long=True, **kwargs)
    cmd = ["growlnotify"] + args
    runcmd.run(cmd)._raise()

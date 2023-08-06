#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from public import public
import runcmd


@public
def get(path=None):
    if not path:
        path = os.getcwd()
    cmd = ["git", "status", "-s"]
    r = runcmd.run(cmd, cwd=path)._raise()
    return r.out


@public
class Status:
    path = None
    out = None

    def __init__(self, path=None):
        if not path:
            path = os.getcwd()
        self.path = path
        self.out = get(path)

    def startswith(self, string):
        lines = []
        for line in self.out.splitlines():
            if line.find(string) == 0:
                lines.append(" ".join(line.split(" ")[2:]))
        return lines

    @property
    def D(self):
        return self.startswith(" D")

    @property
    def d(self):
        return self.D

    @property
    def M(self):
        return self.startswith(" M")

    @property
    def m(self):
        return self.M

    @property
    def R(self):
        return self.startswith(" R")

    @property
    def r(self):
        return self.R

    @property
    def A(self):
        return self.startswith(" A")

    @property
    def a(self):
        return self.A

    @property
    def untracked(self):  # ?? path/to/file
        return self.startswith(" ??")

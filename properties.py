#!/usr/bin/python
# -*- coding: utf-8 -*-
'''用于在Python中模拟其他语言中的数组型Class Property'''


class properties(object):
    def __init__(self, fget=None, fset=None):
        self.fget = fget
        self.fset = fset
        self.obj = None

    def __get__(self, instance, owner):
        self.obj = instance
        return self

    def __getitem__(self, item):
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(self.obj, item)

    def __setitem__(self, key, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(self.obj, key, value)

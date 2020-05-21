#!/usr/bin/python
# -*- coding: utf-8 -*-
'''MVC中的M'''

from properties import properties
from enum import Enum
from EElevator import *


class EModel:
    def __init__(self):
        self._elev = [EElevator(eid) for eid in range(5)]
        self._up = [0 for i in range(20)]
        self._down = [0 for i in range(20)]
        self._goto = [[0 for i in range(20)] for eid in range(5)]

    def __getstatus(self, e):
        elev = self._elev[e]
        if elev.disable:
            return state_t.STAT_DISABLED
        elif elev.timeout:
            return state_t.STAT_DOCKING  # docking
        elif len(elev.route) <= 1:
            return state_t.STAT_FREE  # free
        elif elev.route[0][0] < elev.route[1][0]:
            return state_t.STAT_UP  # up
        else:
            return state_t.STAT_DOWN  # down

    def __setdisable(self, key, value):
        self._elev[key].disable = value

    def __setwaiting(self, key, value):
        status = self.status[key]
        if status == state_t.STAT_FREE or status == state_t.STAT_DOCKING:
            self._elev[key].timeout = value

    def __outRequest(self, reqpos, reqdir):
        '''reqdir == REQ_UP | REQ_DOWN'''
        _updown = self._up if reqdir == req_t.REQ_UP else self._down
        if not _updown[reqpos]:
            _updown[reqpos] = 1
            # dispatch
            mindist, u = 10000, None
            for i in range(5):
                if self._elev[i].disable:
                    continue
                dist = self._elev[i].distance(reqpos, reqdir)
                print(' - %d号电梯距离为%d' % (i+1, dist))
                if dist < mindist:
                    mindist, u = dist, i
            if u is None:
                print(' -> 当前无电梯可用!')
                _updown[reqpos] = 0
                return
            print(' -> 选择%d号电梯' % (u+1))
            self._elev[u].request(reqpos, reqdir)

    def __inRequest(self, e, i):
        if not self._goto[e][i]:
            self._goto[e][i] = 1
            self._elev[e].request(i, req_t.REQ_NOSPEC)
            if self._elev[e].route[0][0] == i:
                self._elev[e].timeout = TIMEOUT

    # Properties
    # 向上请求按钮
    up = properties(lambda self, key: self._up[key],
                    lambda self, key, value: self.__outRequest(key, req_t.REQ_UP))
    # 向下请求按钮
    down = properties(lambda self, key: self._down[key],
                      lambda self, key, value: self.__outRequest(key, req_t.REQ_DOWN))
    # 当前层数
    level = properties(lambda self, key: self._elev[key].route[0][0])

    # 电梯当前状态
    status = properties(lambda self, key: self.__getstatus(key))

    # 电梯等待时间
    wait = properties(lambda self, key: self._elev[key].timeout,
                      lambda self, key, value: self.__setwaiting(key, value))

    # 是否已被禁用
    disable = properties(lambda self, key: self._elev[key].disable,
                         lambda self, key, value: self.__setdisable(key, value))

    #
    goto = properties(lambda self, key: getattr(self, '_goto'+str(key)))
    _goto0 = properties(lambda self, key: self._goto[0][key], lambda self, key, value: self.__inRequest(0, key))
    _goto1 = properties(lambda self, key: self._goto[1][key], lambda self, key, value: self.__inRequest(1, key))
    _goto2 = properties(lambda self, key: self._goto[2][key], lambda self, key, value: self.__inRequest(2, key))
    _goto3 = properties(lambda self, key: self._goto[3][key], lambda self, key, value: self.__inRequest(3, key))
    _goto4 = properties(lambda self, key: self._goto[4][key], lambda self, key, value: self.__inRequest(4, key))

    def update(self):
        '''根据当前的状态得出下一个状态'''
        for i in range(5):
            elev = self._elev[i]
            if elev.disable:
                continue

            ret = elev.update()

            curpos = elev.route[0][0]
            self._goto[i][curpos] = 0

            if self.status[i] == state_t.STAT_DOCKING:
                if len(elev.route) <= 1:
                    self._up[curpos] = 0
                    self._down[curpos] = 0
                elif curpos < elev.route[1][0]:
                    self._up[curpos] = 0
                elif curpos > elev.route[1][0]:
                    self._down[curpos] = 0


if __name__ == '__main__':
    model = EModel()
    while True:
        for i in range(5):
            for a in model._elev[i].route:
                print(a[0], ('↑' if a[1] == req_t.REQ_UP else '↓' if a[1] == req_t.REQ_DOWN else '-'), end=' ')
            print()

        # 0-19 0-4 b电梯a楼
        # a 0 a楼上/下
        try:
            op = input('>>').split()
            if not op:
                model.update()
            elif op[0] == 'A':
                e = int(op[1])
                i = int(op[2])
                model.goto[e][i] = 1
            else:
                reqpos = int(op[0])
                reqdir = int(op[1])
                if reqdir == 1:
                    model.up[reqpos] = 1
                elif reqdir == -1:
                    model.down[reqpos] = 1
        except:
            continue

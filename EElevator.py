#!/usr/bin/python
# -*- coding: utf-8 -*-
''' 单个电梯的模型 '''
from enum import Enum

# 请求类别
req_t = Enum('req_t', ('REQ_UP', 'REQ_DOWN', 'REQ_NOSPEC'))

# 电梯状态
state_t = Enum('state_t', ('STAT_FREE', 'STAT_UP', 'STAT_DOWN', 'STAT_DISABLED', 'STAT_DOCKING'))

# 等待时间
TIMEOUT = 5  # 默认停靠时间
TIMEOUT_SHORTEN = 3  # 按关门键后的等待时间
TIMEOUT_LONGEN = 8  # 按开门键后的等待时间


def req(x):
    ''' 根据x的正负返回REQ_UP/DOWN/NOSPEC '''
    return req_t.REQ_UP if x > 0 else req_t.REQ_DOWN if x < 0 else req_t.REQ_NOSPEC


def conflict(d1, d2):
    '''判断方向是否冲突'''
    return d1 != req_t.REQ_NOSPEC and d1 != d2


def between(a, x, b):
    return a < x < b or a > x > b


class EElevator(object):
    '''单个电梯类'''

    def __init__(self, eid):
        self.eid = eid
        self.route = [(0, req_t.REQ_NOSPEC)]  # 最重要的数据结构, 表示电梯运行的路径, 第二项表示设定的运行方向
        self.timeout = 0
        self.disable = 0

    def request(self, reqpos, reqdir):
        for i in range(len(self.route)):
            r1, d1 = self.route[i]
            r2, d2 = self.route[i+1] if i+1 < len(self.route) else (r1, req_t.REQ_NOSPEC)
            r3, d3 = self.route[i+2] if i+2 < len(self.route) else (r2, req_t.REQ_NOSPEC)
            s1 = req(r2-r1)
            s2 = req(r3-r2)
            if r1 == reqpos and (not conflict(reqdir, s1) or not conflict(s1, reqdir)):
                self.route.insert(i+1, (reqpos, reqdir))
                return
            elif between(r1, reqpos, r2) and not conflict(reqdir, s1):
                self.route.insert(i+1, (reqpos, reqdir))
                return
            elif s1 != s2 and between(r1, r2, reqpos):  # 电梯掉头延长
                if d2 == s1 or d2 == req_t.REQ_NOSPEC:
                    self.route.insert(i+2, (reqpos, reqdir))
                else:
                    self.route.insert(i+1, (reqpos, reqdir))
                return
        self.route.append((reqpos, reqdir))
        return

    def distance(self, reqpos, reqdir):
        count = 0
        for i in range(len(self.route)):
            r1, d1 = self.route[i]
            r2, d2 = self.route[i+1] if i+1 < len(self.route) else (r1, req_t.REQ_NOSPEC)
            r3, d3 = self.route[i+2] if i+2 < len(self.route) else (r2, req_t.REQ_NOSPEC)
            s1 = req(r2-r1)
            s2 = req(r3-r2)
            if r1 == reqpos and (not conflict(reqdir, s1) or not conflict(s1, reqdir)):
                return count
            elif between(r1, reqpos, r2) and not conflict(reqdir, s1):
                return count+abs(reqpos-r1)
            elif s1 != s2 and between(r1, r2, reqpos):  # 电梯掉头延长
                if d2 == s1 or d2 == req_t.REQ_NOSPEC:
                    return count+abs(reqpos-r2)
                else:
                    return count+abs(reqpos-r1)
            count += abs(r2-r1)
        return count+abs(reqpos-self.route[-1][0])

    def update(self):
        '''电梯运行一步(相当于过了一秒钟), 返回电梯的动作'''
        if self.timeout:
            self.timeout -= 1
            return
        if len(self.route) <= 1:
            return
        newd = req(self.route[1][0]-self.route[0][0])
        self.route[0] = self.route[0][0] + (1 if newd == req_t.REQ_UP else -1 if newd == req_t.REQ_DOWN else 0), newd
        if self.route[0][0] == self.route[1][0]:
            print('%d号电梯到达%d楼' % (self.eid+1, self.route[0][0]+1))
            self.timeout = TIMEOUT
            self.route.pop(0)
        return newd

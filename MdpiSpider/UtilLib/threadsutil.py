#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2021 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
自定义线程类和一些多线程方法

Authors: zhangkang06(zhangkang06@baidu.com)
Date:    2021/10/19 11:22:05
"""

import threading


class MyThread(threading.Thread):
    def __init__(self, func, args=(), name='某一线程'):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.name = name
        self.result = None

    # 在执行函数的同时，把结果赋值给result
    def run(self):
        self.result = self.func(*self.args)

    # 然后通过get_result函数获取返回的结果
    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print(e)
            return None


def wait_time_async_run(t, fun, args=None):
    """
    定时器
    :param t: 时间，单位s
    :param fun: 函数
    :param args: 参数
    :return:
    """
    if args is None:
        timer = threading.Timer(float(t), fun)
    else:
        timer = threading.Timer(float(t), fun, args=args)
    timer.start()
    return timer

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2021 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
日志工具类

Authors: zhangkang06(zhangkang06@baidu.com)
Date:    2021/10/19 11:22:05
"""

import os
import logging
import datetime


def get_logger(tag=None, need_write=True):
    """
    method of creating logger
    :param tag: TAG
    :param path1: log_file_path
    :return: logger
    """
    # 记录器
    logger = logging.getLogger(tag)
    logger.setLevel(logging.DEBUG)

    # 屏幕处理器
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)

    # formatter格式
    if tag is not None:
        formatter = logging.Formatter('%(asctime)s  %(levelname)-7s '
                                      '%(filename)15s line %(lineno)4s｜ '
                                      '%(name)-15s:  %(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s  %(levelname)-7s '
                                      '%(filename)-25s line %(lineno)s｜ ' +
                                      ' ' * 13 +
                                      '  %(message)s')
    log_file_name = None
    if need_write:
        log_file_name = verify_log_file()

    # 文件处理器
    fileHandler = None
    if log_file_name is not None:
        fileHandler = logging.FileHandler(filename=log_file_name, encoding=None, delay=False)
        fileHandler.setLevel(logging.DEBUG)

    # 给处理器设置格式
    consoleHandler.setFormatter(formatter)
    if fileHandler:
        fileHandler.setFormatter(formatter)

    # 给记录器设置处理器
    logger.addHandler(consoleHandler)
    if fileHandler:
        logger.addHandler(fileHandler)
    return logger


TAG = 'Logger'
special_logger = logging.getLogger(TAG)


def verify_log_directory():
    desktop = os.path.expanduser('~/Desktop/')
    show_product_path = os.path.join(desktop, "Show端工具产物")
    try:
        if not os.path.exists(show_product_path):
            os.mkdir(show_product_path)
        else:
            special_logger.info(f'文件夹：{show_product_path} 已创建')
    except:
        special_logger.info(f'文件夹：{show_product_path} 创建失败')

    log_directory = os.path.join(show_product_path, "log")
    try:
        if not os.path.exists(log_directory):
            os.mkdir(log_directory)
        else:
            special_logger.info(f'文件夹：{log_directory} 已创建')
    except:
        special_logger.info(f'文件夹：{log_directory} 创建失败')

    return log_directory


def verify_log_file():
    new_log_file = None
    log_directory = verify_log_directory()
    today = datetime.datetime.today().strftime("%Y-%m-%d")
    postfix = '.log'
    today_log_file_name = os.path.join(log_directory, today + '-0' + postfix)
    if os.path.exists(today_log_file_name):
        if os.path.getsize(today_log_file_name) / 1000 / 1000 < 30:
            new_log_file = today_log_file_name
        else:
            today_log_ls = []
            log_ls = os.listdir(log_directory)
            for log_file_name in log_ls:
                if log_file_name.startswith(today):
                    today_log_ls.append(log_file_name)
            today_log_ls.sort()
            latest_file_name = today_log_ls[-1]
            latest_file = os.path.join(log_directory, latest_file_name)
            if os.path.getsize(latest_file) / 1000 / 1000 >= 30:
                new_index = int(latest_file_name.split("-")[-1].strip(postfix)) + 1
                new_log_file = os.path.join(log_directory, today + '-' + str(new_index)) + postfix
            else:
                new_log_file = latest_file
    else:
        new_log_file = today_log_file_name

    return new_log_file


if __name__ == '__main__':
    logger = get_logger('zk')
    logger.info('zk1')
    logger.info('zk2')
    today = datetime.datetime.today().strftime("%Y-%m-%d")

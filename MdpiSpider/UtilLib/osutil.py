#!/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2021 Baidu.com, Inc. All Rights Reserved
#
################################################################################
"""
system命令工具类

Authors: zhangkang06(zhangkang06@baidu.com)
Date:    2021/10/19 11:22:05
"""

import datetime
import os
import signal
import subprocess
import time
import json
from UtilLib import logutil
from UtilLib import threadsutil


class OsUtil:
    TAG = 'OsControler'
    logger = logutil.get_logger(TAG, need_write=False)

    def __init__(self):
        """初始化方法暂时用不到"""
        pass

    @staticmethod
    def timeout_command(command, timeout=20):
        """
        定时执行逻辑
        :param command:命令
        :param timeout:单位s
        :return:
        """
        start = datetime.datetime.now()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while process.poll() is None:
            now = datetime.datetime.now()
            if (now - start).seconds >= timeout:
                try:
                    os.killpg(process.pid, signal.SIGUSR1)
                    os.kill(process.pid, signal.SIGKILL)
                    os.waitpid(-1, os.WNOHANG)
                    process.terminate()
                except Exception:
                    return None
            time.sleep(0.2)
        ans = process.stdout.read().decode('utf-8')
        if process.stdin:
            process.stdin.close()
        if process.stdout:
            process.stdout.close()
        if process.stderr:
            process.stderr.close()
        try:
            process.kill()
        except OSError:
            pass
        try:
            os.killpg(process.pid, signal.SIGUSR1)
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(-1, os.WNOHANG)
            process.terminate()
        except Exception:
            pass
        return ans

    @staticmethod
    def execute_command(command):
        """
        执行终端单行命令
        :param command: 单行命令
        :return:
        """
        OsUtil.logger.info(f'Terminal execute command: {command} ')
        out = os.popen(command)
        return out.read()

        # return OsUtil.timeout_command(command, 10)

    @classmethod
    def get_devices_sn(cls):
        """
        获取设备sn
        @return: sn_list
        """
        sn_list = []
        info = cls.execute_command('adb devices')
        list_of_info = info.split('\n')
        for num, line in enumerate(list_of_info):
            # OsUtil.logger.info(line, num)
            if num > 0 and line != '':
                # 根据制表符的index来截取设备的sn
                index_of_tab = line.index('\t')
                sn_list.append(line[:index_of_tab])
        OsUtil.logger.info('sn_list：' + str(sn_list))
        threadsutil.wait_time_async_run(0.5, fun=OsUtil.install_uiautomator_for_all, args=(sn_list,))
        return sn_list

    @classmethod
    def cat_and_grep(cls, file_name, grep_field=None, nums_of_fb_rows=1):
        if grep_field is not None:
            command = 'cat ' + file_name + ' |grep -C' + str(nums_of_fb_rows) + ' ' + '"' + grep_field + '"'
            res = cls.execute_command(command)
        else:
            command = 'cat ' + file_name
            res = cls.execute_command(command)
        return res

    @classmethod
    def pull_log(cls, parent_directory, device_sn):
        try:
            OsUtil.logger.info('正在从设备中拉取log日志，请稍等一分钟')
            command = f'adb -s {device_sn} pull data/log {parent_directory}'
            pull_log_res = cls.execute_command(command)
            OsUtil.logger.info(pull_log_res)
            command = f'adb -s {device_sn} pull data/anr {parent_directory}'
            pull_anr_res = cls.execute_command(command)
            OsUtil.logger.info(pull_anr_res)
            if 'error' not in pull_log_res:
                OsUtil.logger.info(f'拉取log日志到： {parent_directory} 成功')
            else:
                OsUtil.logger.info(f'拉取log日志失败')
                return False
            if 'error' not in pull_anr_res:
                OsUtil.logger.info(f'拉取anr日志到： {parent_directory} 成功')
            else:
                OsUtil.logger.info(f'拉取anr日志失败')

            return parent_directory

        except:
            OsUtil.logger.exception('请连接设备，如已连接请确认设备权限')

    @classmethod
    def clear_device_log(cls, device):
        command = f'adb -s {device} root'
        res = OsUtil.execute_command(command)
        OsUtil.logger.info(res)
        OsUtil.logger.info('清除设备日志')
        command = f'adb -s {device} shell rm -rf data/log/*'
        OsUtil.execute_command(command)

    @classmethod
    def get_rom_version(cls, device_sn):
        try:
            OsUtil.logger.info('正在获取设备的Rom版本')
            command = 'adb -s ' + device_sn + ' ' + 'shell getprop |grep desc'
            line = cls.execute_command(command)
            OsUtil.logger.info(line)
            line_list = line.split(':')
            rom_version = line_list[-1].strip('\n')
            OsUtil.logger.info(f'设备的Rom版本为： {rom_version} \n')
            return rom_version
        except Exception as e:
            OsUtil.logger.info(e)
            OsUtil.logger.info('请连接设备，如已连接请确认设备权限')

    @classmethod
    def get_launcher_version(cls, device_sn):
        try:
            OsUtil.logger.info('正在获取设备的launcher版本')
            command = 'adb -s ' + device_sn + ' ' + 'shell dumpsys package com.baidu.launcher |grep versionName'
            res = cls.execute_command(command)
            OsUtil.logger.debug(f'\n{res}')
            version_info_list = res.split('\n')
            OsUtil.logger.debug(f'version_info_list：{version_info_list}, 长度：{len(version_info_list)}')
            if len(version_info_list) >= 2:
                line1 = version_info_list[0]
                line1_list = line1.split('=')
                data_launcher_version = line1_list[-1].strip('\n')
                OsUtil.logger.info(f'{device_sn} data分区的launcher版本为： {data_launcher_version}')
                line2 = version_info_list[1]
                line2_list = line2.split('=')
                system_launcher_version = line2_list[-1].strip('\n')
                OsUtil.logger.info(f'{device_sn} system分区的launcher版本为： {system_launcher_version}')
                if data_launcher_version <= system_launcher_version:
                    launcher_version = system_launcher_version
                else:
                    launcher_version = data_launcher_version
            else:
                line1 = version_info_list[0]
                line1_list = line1.split('=')
                launcher_version = line1_list[-1].strip('\n')
            launcher_version = f'[{launcher_version}]'
            OsUtil.logger.info(f'设备 {device_sn} 的launcher版本为： {launcher_version} \n')
            return launcher_version
        except Exception as e:
            OsUtil.logger.info(e)
            OsUtil.logger.info('请连接设备，如已连接请确认设备权限')

    @classmethod
    def remove_with_path(cls, directory):
        try:
            if os.path.exists(directory):
                command = 'rm -rf' + ' ' + directory
                cls.execute_command(command)
                OsUtil.logger.info(f'删除文件： {directory}')
        except Exception as e:
            OsUtil.logger.info(e)
            OsUtil.logger.info('删除失败')

    @classmethod
    def creat_directory(cls, directory):
        try:
            if not os.path.exists(directory):
                os.mkdir(directory)
                OsUtil.logger.info(f'创建文件夹：{directory}')
            else:
                OsUtil.logger.info(f'文件夹：{directory} 已创建')
        except:
            OsUtil.logger.error(f'文件夹：{directory} 创建失败')

    @classmethod
    def creat_directory(cls, directory):
        try:
            if not os.path.exists(directory):
                os.mkdir(directory)
                OsUtil.logger.info(f'创建文件夹：{directory}')
            else:
                OsUtil.logger.info(f'文件夹：{directory} 已创建')
        except:
            OsUtil.logger.error(f'文件夹：{directory} 创建失败')

    @classmethod
    def creat_file(cls, file):
        try:
            if not os.path.exists(file):
                command = f'touch {file}'
                OsUtil.execute_command(command)
                OsUtil.logger.info(f'创建文件：{file}')
            else:
                OsUtil.logger.info(f'文件：{file} 已创建')
        except:
            OsUtil.logger.error(f'文件：{file} 创建失败')

    @classmethod
    def get_desktop(cls):
        return os.path.expanduser('~/Desktop')

    @classmethod
    def get_user(cls):
        return os.path.expanduser('~')

    @classmethod
    def query_use_broadcast(cls, word, deviceid):
        t = time.time()
        OsUtil.execute_command("adb -s " + deviceid + " shell am broadcast -a com.baidu.duer.query -e q  " + word)
        return time.time() - t

    @classmethod
    def beauty_json(cls, dict_directive):
        beauty_json = json.dumps(dict_directive, ensure_ascii=False, indent=6) \
            .encode('utf-8').decode('utf-8', errors='ignore')
        return beauty_json

    @classmethod
    def install_uiautomator_for_all(cls, devices):
        for device in devices:
            OsUtil.check_uiautomator_exists(device)

    @classmethod
    def check_uiautomator_exists(cls, device):
        command = f"adb -s {device} shell pm list packages"
        package_ls = OsUtil.execute_command(command)
        if "com.github.uiautomator" in package_ls and "com.github.uiautomator.test" in package_ls:
            OsUtil.logger.info('设备中已经安装了 uiautomator 和 uiautomator.test')
            return True
        else:
            install_res, apk = OsUtil.install_uiautomator_for_device(device)
            if install_res == 'Success':
                return True
            else:
                command = f'adb -s {device} install -r -t -d {apk}'
                OsUtil.logger.info('w', f'com.github.uiautomator 安装失败, 请再次尝试或手动安装：\n{command}')
                return False

    @classmethod
    def install_uiautomator_for_device(cls, device):
        com_github_uiautomator = os.path.join(OsUtil.get_desktop(),
                                              'show端工具文件夹/短链数据测试/necessary/third-party/app-uiautomator-test.apk')
        com_github_uiautomator_test = os.path.join(OsUtil.get_desktop(),
                                                   'show端工具文件夹/短链数据测试/necessary/third-party/app-uiautomator.apk')
        command = f'adb -s {device} install -r -t -d {com_github_uiautomator}'
        res = OsUtil.execute_command(command)
        if "Success" in res:
            OsUtil.logger.info('com.github.uiautomator 安装成功')
        else:
            OsUtil.logger.info('com.github.uiautomator 安装失败')
            return False, com_github_uiautomator

        command = f'adb -s {device} install -r -t -d {com_github_uiautomator_test}'
        res = OsUtil.execute_command(command)

        if "Success" in res:
            OsUtil.logger.info('com.github.uiautomator.test 安装成功')
        else:
            OsUtil.logger.info('com.github.uiautomator.test 安装失败')
            return False, com_github_uiautomator_test

        return "Success", None


if __name__ == '__main__':
    '123'.encode('utf-8').decode()

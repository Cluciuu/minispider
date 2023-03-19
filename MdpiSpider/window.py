#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ===============================================================================
#
# Copyright (c) 2021 Baidu.com, Inc. All Rights Reserved
#
# ===============================================================================
"""
模块介绍：

Authors: zhangkang06(zhangkang06@baidu.com)
Date:2022/04/03 23:31:38
"""

# !/usr/bin/env python
# -*- coding: UTF-8 -*-
################################################################################
#
# Copyright (c) 2021 Baidu.com, Inc. All Rights Reserved
#
################################################################################


import os
import time
import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog
from tkinter import ttk
from UtilLib import logutil
from UtilLib import threadsutil
from mdpi_spider import MdpiSpider
import multiprocessing


class MdpiTool(tk.Frame):
    """MdpiTool主界面"""

    TAG = 'MdpiTool'
    logger = logutil.get_logger(TAG, need_write=False)

    def __init__(self, master=None):
        # 把 master 传给 Frame 的构造方法
        super().__init__(master)
        self.master = master
        self.pack()

        # 创建工作目录
        self.product_directory = self.creat_mdpi_total_directory()

        # 创建组件
        self.creat_widget()

        # 组建布局
        self.start_layout()

    def creat_mdpi_total_directory(self):
        root_directory = os.path.join(os.path.expanduser('~/Desktop'), 'MdpiSpiderProduct')
        if not os.path.exists(root_directory):
            os.mkdir(root_directory)
            MdpiTool.logger.info(f'创建文件夹：{root_directory}')
        else:
            MdpiTool.logger.info(f'文件夹：{root_directory} 已存在')

        return root_directory

    def creat_widget(self):
        """
        创建组件
        :return: None
        """
        # 创建Tab Bar
        self.creat_button_and_file_entry()
        self.creat_start_invite_model()

    def creat_button_and_file_entry(self):
        # file_path字符初始化
        self.file_path = tk.StringVar()
        self.password = tk.StringVar()

        # 创建选择文件的label
        self.label_chooseFile = tk.Label(self)
        self.label_chooseFile['text'] = '选择excel文件'
        self.label_chooseFile['font'] = ('微软雅黑', 15)
        self.label_chooseFile['height'] = 1
        self.label_chooseFile['bg'] = 'sienna'
        self.label_chooseFile['fg'] = 'black'
        self.label_chooseFile['borderwidth'] = 2  # 边框宽度
        self.label_chooseFile['relief'] = None  # 边框样式:3D效果包括 raised,sunken,flat,ridge,solid,groove
        self.label_chooseFile['justify'] = 'center'  # 字体对齐方式
        self.label_chooseFile['image'] = None  # 标签图片
        # self.label_chooseFile.pack()

        # 创建选择文件的entry
        self.entry_chooseFile = tk.Entry(self)
        self.entry_chooseFile['textvariable'] = self.file_path
        self.entry_chooseFile['state'] = 'readonly'
        # self.entry_chooseFile.pack()

        # 创建选择文件的Button
        self.btn_chooseFile = tk.Button(self)
        self.btn_chooseFile['text'] = '点击选择目标文件'
        self.btn_chooseFile['command'] = lambda: self.choose_file_function(self.file_path)
        # self.btn_chooseFile.pack()

        # 创建确认密码的label
        self.label_inputPassword = tk.Label(self)
        self.label_inputPassword['text'] = '确认密码'
        self.label_inputPassword['font'] = ('微软雅黑', 15)
        self.label_inputPassword['height'] = 1
        self.label_inputPassword['bg'] = 'sienna'
        self.label_inputPassword['fg'] = 'black'
        self.label_inputPassword['borderwidth'] = 2  # 边框宽度
        self.label_inputPassword['relief'] = None  # 边框样式:3D效果包括 raised,sunken,flat,ridge,solid,groove
        self.label_inputPassword['justify'] = 'center'  # 字体对齐方式
        self.label_inputPassword['image'] = None  # 标签图片
        # self.label_inputPassword.pack()

        # 创建输入密码的entry
        self.entry_inputPassword = tk.Entry(self)
        password = self.get_password_from_password_file()
        self.password.set(password)
        self.entry_inputPassword['textvariable'] = self.password
        self.entry_inputPassword['justify'] = 'center'
        # self.entry_inputPassword['state'] = 'readonly'
        # self.entry_inputPassword.pack()

        # 创建保存密码的Button
        self.btn_savePassword = tk.Button(self)
        self.btn_savePassword['text'] = '保存密码'
        self.btn_savePassword['command'] = lambda: self.save_password()
        # self.btn_savePassword.pack()

    def choose_file_function(self, file_path):
        """
        选择可压缩的文件或者Txt文件
        :return: file_path
        """
        new_path = tk.filedialog.askopenfilename()
        file_path.set(new_path)
        return file_path

    def save_password(self):
        password = self.entry_inputPassword.get()
        if password is not None:
            MdpiTool.logger.info(f"save password: {password}")
        if not os.path.exists(self.product_directory):
            self.creat_mdpi_total_directory()
        else:
            password_file = os.path.join(self.product_directory, 'password')
            with open(password_file, 'w', encoding='utf-8') as file:
                file.write(password)

    def get_password_from_password_file(self):
        password = None
        password_file = os.path.join(self.product_directory, 'password')
        if os.path.exists(password_file):
            with open(password_file, 'r', encoding='utf-8') as file:
                password = file.readlines(1)
        MdpiTool.logger.info(f"get password from file: {password}")
        return password

    def creat_start_invite_model(self):
        """
        创建开始分析模块
        :return: None
        """
        # 创建一个开始分析的Button
        self.btn_startInvite = tk.Button(self, font=('黑体', 15, 'bold'))
        self.btn_startInvite['text'] = '开始邀请'
        self.btn_startInvite['command'] = lambda: threadsutil.wait_time_async_run(0.2, fun=self.start_invite)
        self.btn_startInvite['fg'] = 'blue'
        # self.btn_Start.pack()

    def start_invite(self):
        excel_file = self.entry_chooseFile.get()
        if not excel_file:
            self.display_msgbox('i', '没有选择要检测的文件')
        else:
            MdpiTool.logger.info(f'excel_file: {excel_file}')
            password = self.entry_inputPassword.get()
            if password is not None and password != " ":
                self.save_password()
                mdpi_spider = MdpiSpider(excel_file, password)
                mdpi_spider.start_work()
            else:
                MdpiTool.logger.info('不正确的密码')

    def start_layout(self):
        """
        布局管理
        @return: None
        """
        # 顶部空白模块布局
        # self.topBlack.grid(row=0, column=0, sticky='w', padx=10, pady=15)
        # 文件分析模块布局
        self.label_chooseFile.grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.entry_chooseFile.grid(row=0, column=1, sticky='we', padx=10, pady=10)
        self.btn_chooseFile.grid(row=0, column=2, sticky='we', padx=10, pady=10)
        self.label_inputPassword.grid(row=1, column=0, sticky='we', padx=10, pady=10)
        self.entry_inputPassword.grid(row=1, column=1, sticky='w', padx=10, pady=10)
        self.btn_savePassword.grid(row=1, column=2, sticky='we', padx=10, pady=10)
        self.btn_startInvite.grid(row=3, column=1, sticky='we', padx=10, pady=10, ipady='15')

    def display_msgbox(self, msg_level, msg):
        """
        显示不同类型的对话框
        @return: None
        """
        # info
        if msg_level == 'i':
            self.msgbox = messagebox.showinfo(title='MdpiTool', message=msg)
            MdpiTool.logger.info(msg)

        # warning
        if msg_level == 'w':
            self.msgbox = messagebox.showwarning(title='MdpiTool', message=msg)
            msg = '\033[1;31m' + msg + '\033[0m'
            MdpiTool.logger.info(msg)

        # error
        if msg_level == 'e':
            self.msgbox = messagebox.showerror(title='MdpiTool', message=msg)
            msg = '\033[1;31m' + msg + '\033[0m'
            MdpiTool.logger.info(msg)


if __name__ == '__main__':
    t = time.time()
    # 创建主窗口
    root_window = tk.Tk()
    root_window.geometry('600x200+450+200')

    # 窗口标题
    root_window.title('MdpiTool 1.0')
    root_window['background'] = 'burlywood'

    # 创建一个app
    app = MdpiTool(master=root_window)
    app['background'] = 'burlywood'
    app.place(relx=0.1)

    # 关闭窗口时要关闭代理，不然下一次端口会被占用
    # root_window.protocol('WM_DELETE_WINDOW', lambda: Func.stop_mitm_and_destroy(app))

    # 主窗口的循环刷新
    root_window.mainloop()


#self.label_inputPassword.grid(row=1, column=0, sticky='w', padx=10, pady=20)
 #       self.entry_chooseFile.grid(row=1, column=0, sticky='w', padx=10, pady=20)

if __name__ == '__main__':
    multiprocessing.freeze_support()

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
Date:2022/04/03 21:02:12
"""

import datetime
import pytz
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from lxml import etree

# paris_strft_time_now = datetime.datetime.now(pytz.timezone('Europe/Paris')).strftime('%Y-%m-%d %H:%M:%S')
# timedelta = datetime.timedelta(days=90) - (datetime.datetime.strptime(paris_strft_time_now, "%Y-%m-%d %H:%M:%S") - \
#             datetime.datetime.strptime('2022-01-03 19:00:00', "%Y-%m-%d %H:%M:%S"))
# print(f'timedelta: {timedelta}')
# print(timedelta > datetime.timedelta(days=0, hours=4))


session = requests.session()
url = 'https://login.mdpi.com'
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
response = session.get(url=url)
selector = etree.HTML(response.text)
csrf_token = selector.xpath('//input[@name="_csrf_token"]/@value')[0]
print(f'csrf_token: {csrf_token}')

post_data = {"_username": "lilla.liang@mdpi.com",
                     "_password": 'T9HuThgvD2XLhuf',
                     "_target_path": "https://login.mdpi.com/",
                     "_csrf_token": csrf_token

                     }
url = 'https://login.mdpi.com/login_check'
# url = response.url
response = session.post(url=url, data=post_data, verify=False)
print(f'login response.status_code: {response.status_code}')


url = 'https://susy.mdpi.com/special_issue_pending/list'
response = session.get(url=url, timeout=3)
# print(response.text)
sselector = etree.HTML(response.text)
all_issue_ls = sselector.xpath('//tr[@data-id]')
print(f'issue_ls : {all_issue_ls}')


available_issue_list = []
for issue_item in all_issue_ls:
    # issue id
    issue_item_id = issue_item.get('data-id')
    issue_item_children = list(issue_item)
    # issue名称 = issue_item_children[1]
    issue_name_ls = list(issue_item_children[1])
    issue_name = issue_name_ls[0].text
    # issue状态 = issue_item_children[5]
    print(f'{issue_item_id:7}【 {issue_name:70} 】｜ status: {issue_item_children[5].text}')
    if 'Pending GE invitation' in issue_item_children[5].text:
        available_issue_list.append((issue_item_id, issue_name))
print(f'available_issue_list:{available_issue_list}')
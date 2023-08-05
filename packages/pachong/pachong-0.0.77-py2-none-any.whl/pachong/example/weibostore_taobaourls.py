#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/28/18
# @File  : [pachong] weibostore_taobaourls.py


from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from pachong.crawler import Weibo
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Requests
from pushbullet import PushBullet


# args = sys.argv[1:]
# i_file = args[0]
username = '0016095945117'

fetcher = Requests()
# crawler = Weibo('yizhibo', 'weibo_users', fetcher=fetcher, Database=MongoDB).import_input('weibousers{}.json'.format(i_file), is_json=True)
crawler = Weibo('wanghong', 'taobaodianzhu', fetcher=fetcher, Database=MongoDB)
last = 99999
while True:
    try:
        crawler.login(username, 'Ccc19900201')
    except:
        continue
    crawler.crawl('weibostore')
    if len(crawler.samples) == 0 or last == len(crawler.samples):
        # pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
        # pb.push_note('weibo profile{}'.format(i_file), 'done')
        break
    last = len(crawler.samples)

last = 99999
while True:
    # crawler = Weibo('wanghong', 'users_full', fetcher=fetcher, Database=MongoDB)
    # try:
    #     crawler.login(username, 'Cc19900201')
    # except:
    #     continue
    crawler.crawl('profile')
    if len(crawler.samples) == 0 or last == len(crawler.samples):
        # pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
        # pb.push_note('weibo store{}'.format(i_file), 'done')
        break
    last = len(crawler.samples)

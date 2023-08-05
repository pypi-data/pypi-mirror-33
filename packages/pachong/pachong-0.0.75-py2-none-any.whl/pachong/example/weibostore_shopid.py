#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/22/18
# @File  : [pachong] weibostore_shopid.py


from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Requests
from pushbullet import PushBullet
import sys

i_file = int(sys.argv[1])

project = 'wanghong'
# project = 'test'
input_ = 'taobaodianzhu'
fetcher = Requests()
Taobao(project, input_, fetcher=fetcher, Database=MongoDB).import_input('taobaodianzhu{}.json'.format(i_file), is_json=True)
last_=9999
while True:
    crawler = Taobao(project, input_, fetcher=fetcher, Database=MongoDB)
    crawler.crawl('shopid_from_weibostore')
    this_=len(crawler.samples)
    if this_==0 or this_ == last_:
        break
    last_ = this_

pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
pb.push_note('shopid{}'.format(i_file), 'done')

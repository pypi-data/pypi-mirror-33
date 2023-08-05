#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/28/18
# @File  : [pachong] weibo_searchusers.py


from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler import Weibo
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser

# .import_input(input_list=['#微博橱窗#', '上新', '淘宝店铺号'], update=True) \
fetcher = Browser('firefox')
crawler = Weibo('wanghong', 'searchkeywords_taobaousers', output='taobaodianzhu', fetcher=fetcher, Database=MongoDB) \
    .import_input(input_list=['淘宝店主', '淘宝店铺号'], update=True) \
    .login('0012028475117', 'Ccc19900201')

raw_input('any')
crawler.crawl('searchusers')
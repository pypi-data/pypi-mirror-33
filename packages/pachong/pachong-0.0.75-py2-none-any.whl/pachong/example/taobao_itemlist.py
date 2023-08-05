#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/3/18
# @File  : [pachong] taobao_itemlist.py



from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler import Taobao
from pachong.database import MongoDB
from pachong.fetcher import Browser

fetcher = Browser('firefox')
# fetcher = Browser(proxy='13.56.211.230:3128')
crawler = Taobao('wanghong', 'taobao_shops2', output='taobao_items2', fetcher=fetcher, Database=MongoDB) \
    .login()
# .set_pushbullet('o.cJm1iLu3sJtvm7P0YIHuBvy8lpYtPOIQ') \


crawler.crawl('itemlist')
fetcher.session.close()

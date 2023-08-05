#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/6/18
# @File  : [pachong] taobao_comments.py


from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser
from pushbullet import PushBullet

args = sys.argv[1:]
nfile = int(args[0])

# with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/inputs/itemids16.txt', 'r') as i:
#     input_list = [line.strip() for line in i if line.strip()]

fetcher = Browser('firefox', use_network=True, load_images=False)
crawler = Taobao('yizhibo3', 'taobao_items', output='taobao_comments', fetcher=fetcher, Database=MongoDB)#.login()
#     # .import_input('itemids{}.txt'.format(nfile))#.import_input(input_list=['559667455412'])
crawler.crawl('comments')
fetcher.session.close()

pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
pb.push_note('taobao_items'.format(nfile), 'done')
# fetcher = Browser('firefox')
# crawler = Taobao('wanghong', 'taobao_items', 'taobao_comments', fetcher=fetcher, Database=MongoDB)
#     # .import_input(input_list=input_list, update=True)
# crawler.crawl('itempage')
# fetcher.session.close()


# import json
# count = 20
# with open('/Users/cchen/Downloads/wh/users2.json', 'r') as i:
#     for line in i:
#         jline = json.loads(line)
#         if jline.get('task', {}).get('timeline', {}).get('status', '') != 'done':
#             count += 1
#             with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/inputs/users{}.json'.format(count), 'w') as o:
#                 o.write(line)

# from pachong.fetcher import Requests
# fetcher = Requests()
# html = fetcher.get('https://www.yizhibo.com/l/nPidB_QfXTu3kxK5.html')
# fetcher.find('script', type='text/javascript')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/14/18
# @File  : [pachong] weibo_timeline.py

from __future__ import absolute_import
from __future__ import unicode_literals

import sys

from pachong.crawler import Weibo
from pachong.database import MongoDB
from pachong.fetcher import Requests
from pushbullet import PushBullet
import random

args = sys.argv[1:]
i_file = args[0]

project = 'wanghong'
# project = 'test'
input_ = 'users'
# username = '0012028475117'
usernames = ['0016095945117', '0012028475117']
username = random.sample(usernames, 1)[0]

# input_ = 'taobaodianzhu'
# fetcher = Requests(proxy="localhost:3128")
fetcher = Requests()
crawler = Weibo(project, input_, fetcher=fetcher, Database=MongoDB) \
    .import_input(filepath='weibousers{}.json'.format(i_file), is_json=True)
while True:
    fetcher = Requests()
    crawler = Weibo(project, input_, fetcher=fetcher, Database=MongoDB)
    try:
        crawler = crawler.login(username, 'Ccc19900201')
    except:
        continue

        # .import_input(input_list=['1866833821'], update=True)

    # crawler.crawl('profile')
    output = 'timeline'
    crawler.output = output
    crawler.crawl('timeline')
    if len(crawler.samples) == 0:
        break

pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
pb.push_note('User{}'.format(i_file), 'done')


# # self=crawler
# from tqdm import tqdm
# tl = MongoDB('wanghong', 'timeline')
# with tqdm(tl.get_all(), miniters=10000) as bar:
#     for row in bar:
#         mid = row['_id']
#         # likes = row.get('likes', '')
#         # comments = row.get('comments')
#         # forwards = row.get('forwards')
#         # if not likes:
#         #     tl.drop_field(mid, 'likes')
#         # else:
#         #     tl.update(mid, {'likes': int(likes)})
#         # if not comments:
#         #     tl.drop_field(mid, 'comments')
#         # else:
#         #     tl.update(mid, {'comments': int(comments)})
#         # if not forwards:
#         #     tl.drop_field(mid, 'forwards')
#         # else:
#         #     tl.update(mid, {'forwards': int(forwards)})
#         text = row['text'].strip('\u200b \t')
#         tl.update(mid, {'text': text})
#         # urls = row.get('urls', [])
#         # if not urls:
#         #     tl.drop_field(mid, 'urls')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/6/18
# @File  : [pachong] taobao_itempage.py


from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import traceback
from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser, Requests
from pushbullet import PushBullet
from pachong.crawler.common.exceptions import TaskDoneOther
from tqdm import tqdm

args = sys.argv[1:]
i_file = int(args[0])
# batch = int(args[1])

fetcher = Browser('firefox', use_network=True, load_images=False)
db_in = MongoDB('yizhibo', 'taobao_items')
db_out = MongoDB('yizhibo', 'taobao_comments')
with open('inputs/items{}.txt'.format(i_file)) as i:
    input_list = {line.strip() for line in i if line.strip()} - \
                 {doc['_id'] for doc in db_in.find_all({'task.comments.status': 'done'})}

last = len(input_list)
while True:
    crawler = Taobao('yizhibo', 'taobao_items', output='taobao_comments', fetcher=fetcher, Database=MongoDB)
    success = set()
    with tqdm(input_list) as bar:
        for target in bar:
            db_in.insert({'_id': target})
            bar.set_description(target)
            try:
                [db_out.insert(chong)
                 for chong in crawler.comments({'_id': target})
                 if chong]
                db_in.update(target, {'task.comments.status': 'done'})
                db_in.drop_field(target, 'task.comments.traceback')
                success.add(target)
            except TaskDoneOther as taskdone_error:
                success.add(target)
                db_in.update(target, {'task.comments.status': 'done',
                                      'task.comments.other': taskdone_error.other})
            except KeyboardInterrupt:
                fetcher.session.close()
                sys.exit(0)
            except Exception:
                db_in.update(target, {'task.comments.status': 'error',
                                      'task.comments.traceback': traceback.format_exc()})
    input_list -= success
    this_ = len(input_list)
    if this_ == last:
        break
    last = this_

fetcher.session.close()
pb = PushBullet('o.EXRbEibhhzjtfJdYuhseaWZDfeq3FLvo')
pb.push_note('taobao{}'.format(i_file), 'done')

# fetcher = Browser('firefox')
# while True:
#     crawler = Taobao('yizhibo', 'taobao_items', fetcher=fetcher, Database=MongoDB) \
#         .crawl('itempage')
#     fetcher.session.close()
#     if len(crawler.samples) == 0:
#         break
# fetcher.session.close()
#


#
# import re
# import json
# b = a
#
# while True:
#     try:
#         json.loads(a)
#     except ValueError as e:
#         position = int(re.compile('\(char ([0-9]+)\)').search(e.args[0]).group(1))
#         a = re.sub('^' + re.escape(a[:position - 1]) + '\"([^"]+)\"', a[:position - 1] + '\\"\g<1>', a)
#
#
# re.compile('\"content\":\"[^"]+\"[^"]+\"[}]]*,\"').search(a).group(0)
# json.loads(re.sub('(\"content\":\"[^"]+)\"([^"]+\"[}]]*,\")', '\g<1>\g<2>', a))
#
# print re.compile('\"content\":\"(.*?)[}]]*,\"').search(b).group(0)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/16/18
# @File  : [pachong] example_mongodb.py


from pachong.database import MongoDB

db = MongoDB('wanghong', 'users')
print(db.find('2045908335')['weibos'])
db2 = MongoDB('wanghong', 'users_full')

current_ids = [doc for doc in db.find_all({'task.timeline.status': {'$in': [None, 'error']}})]
for doc in db.find_all({}):
    if doc['_id'] in current_ids:
        db2.update(doc['_id'], doc)
    else:
        db2.insert(doc)


n_followers = [doc.get('n_followers', 0) for doc in db2.find_all({})]
import pandas
tar = pandas.DataFrame(n_followers)
tar.describe()


# uids = {user['_id'] for user in a}
# with open('taobaouser_from_weibo.txt', 'w') as o:
#     [o.write(uid + '\n') for uid in uids]

MongoDB('wanghong', 'taobao_items').update('559774227824', )

for item in db2.find_all({'$nor': [{'winfo': {'$regex': '(品牌主理人|工作室创始人)'}},
                                   {'pinfo': {'$regex': '(品牌主理人|工作室创始人)'}}]}):
    db2.drop(item['_id'])

for item in db2.find_all({'$and': [{'n_followers': {'$gte': 338}},
                                   {'n_weibos': {'$gte': 40}}]}):
    db.insert(item)

for item in db.find_all({'task.shopid.status': 'error'},['task.shopid.traceback']):
    print item


a = db.get({'task.timeline.status': 'error'})
print(a['task']['timeline']['traceback'])
test = MongoDB('test', 'user')
for item in test.get_all(): print(item)
test.insert({'_id': 1, 'test': [('h额呵呵', 1), ('啊哈哈哈', 'http')]})
a = test.get(1)
for item in a['test']:
    print(item[0])
    print(item[1])



import pymongo
from sshtunnel import SSHTunnelForwarder

MONGO_HOST = "10.0.1.29"
MONGO_PORT = 27017
MONGO_DB = "test"
MONGO_USER = "cchen"
MONGO_PASS = "Cc19900201"

db = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
db['test']['test'].insert({'b': 'haha'})
a = db['test']['test'].find()
from tqdm import tqdm
with tqdm(a, total=a.count()) as bar:
    for b in bar:
        print(b)
a.count()

a=a.skip(1)
a.next()

db['test']['test'].update_one({'b':'haha'}, {'$set': {'d': 'hehe'}})

server = SSHTunnelForwarder(
    MONGO_HOST,
    remote_bind_address=('127.0.0.1', 27017)
)

server.start()

client = pymongo.MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
db = client[MONGO_DB]
db['test'].insert({'a': 'haha'})

server.stop()




from glob import glob
import random
import math
exclude_list = []
for fp in glob('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/itemids*.txt'):
    with open(fp, 'r') as i:
        exclude_list += [line.strip() for line in i]

db = MongoDB('wanghong', 'taobao_items')
with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/itemids15.txt', 'r') as i:
    samples = [_id.strip() for _id in i if _id.strip()]
docs = [doc for doc in db.find_all({'$or': [{'task.comments.status': {'$nin': ['done']}}, {'task.itempage.status': {'$nin': ['done']}}]})]
#    ,
# '_id': {'$in': samples}})]
# ids = ids[-20000:]
ids = random.sample(ids, len(ids))
len_per_file = len(samples) / 6 / 4
for i_file in range(min(int(math.ceil(len(ids) * 1./len_per_file)), 24)):
    with open('inputs2/itemids{}.txt'.format(i_file), 'w') as f:
        this_ids = ids[i_file * len_per_file: (i_file + 1) * len_per_file]
        [f.write(_id + '\n') for _id in this_ids]

docs = [doc for doc in db.find_all({'task.comments.status': None,
                                    'task.itempage.status': None})]
docs = random.sample(docs, len(docs))
len_per_file = len(docs) / 6 / 4
max_file = 24
import json
for counter, i_file in enumerate(range(min(int(math.ceil(len(docs) * 1./len_per_file)), max_file))):
    with open('inputs2/items{}.txt'.format(i_file + 24), 'w') as f:
        this_docs = docs[i_file * len_per_file: (i_file + 1) * len_per_file] \
            if counter < max_file - 1 else docs[i_file * len_per_file: ]
        [f.write(str(doc) + '\n') for doc in this_docs]
        # [f.write(json.dumps(doc) + '\n') for doc in this_docs]


db = MongoDB('wanghong', 'taobao_comments')
item_ids = {item['itemid'] for item in db.find_all(fields=['itemid'])}
db2 = MongoDB('wanghong', 'taobao_items')
items = [item for item in db2.find_all()]
db2.drop_field({'_id': {'$nin': list(item_ids)}}, 'task.comments')


import json
db = MongoDB('wanghong', 'taobaouser_from_weibo')
with open('inputs/users21.json', 'w') as o:
    for doc in db.find_all({'task.timeline.status': {'$ne': 'done'}}):
        o.write(json.dumps(doc) + '\n')


for fp in glob('/Users/cchen/GoogleDrive/porkspace/*t.json'):
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line.strip())
            _id = jline['_id']
            db.update(_id, jline)


import json
from glob import glob
db = MongoDB('wanghong', 'taobao_items')
# db2= MongoDB('wanghong', 'taobao_comments')
for fp in glob('/Users/cchen/GoogleDrive/porkspace/*item.json'):
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line.strip())
            _id = jline['_id']
            if 'task' not in jline:
                continue
            task = jline.pop('task')
            input_ = db.find(jline['_id'])
            input_task = input_.get('task', {})
            input_task.update(task)
            input_.update(jline)
            input_['task'] = input_task
            db.update(jline['_id'], input_)
            # if jline.get('task', {}).get('comments',{}).get('status') == 'done':
            #     db.update(jline['_id'], {'task.comments.status': 'done'})


db = MongoDB('wanghong', 'users')
db.drop_field_all(field='task.shopid_manual.status')


db.find_all({'task.comments.status': {'$ne':'done'},
             'task.itempage.status': {'$ne': 'done'}}).count()

#
# db1 = MongoDB('wanghong', 'users')
# uids = {target['_id'] for target in db1.find_all(fields=['_id'])}
db2 = MongoDB('wanghong', 'keyweibos')
# for target in db2.find_all(fields=['_id', 'uid']):
#     uids2 = {target['uid'] for target in db2.find_all(fields=['_id', 'uid'])}
#         db2.drop(target['_id'])

db3 = MongoDB('wanghong', 'taobaouser_from_weibo')
db3.drop_field_all('task.profile')
ids = [target['_id'] for target in db3.find_all({'task.weibostore.status': {'$ne': 'done'}}, fields=['_id', 'uid'])]


from glob import glob
db = MongoDB('wanghong', 'taobao_items')
for fp in glob('/Users/cchen/Downloads/wh/taobao_items*.json'):
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line)
            uid = jline['_id']
            db.update(uid, jline)

            # doc = db.find(uid)
            # if doc.get('task', {}).get('timeline', {}).get('status') == 'done':
            #     continue
            # elif doc.get('task', {}).get('timeline', {}).get('page', 0) > jline.get('task', {}).get('timeline', {}).get('page', -1):
            #     continue
            # db.update(uid, jline)

import csv
with open('/Users/cchen/GoogleDrive/porkspace/projects/wanghong/wanghongdata/wanghonglist.tsv') as i:
    csvreader = csv.reader(i, delimiter=str('\t'))
    for nick, uid in csvreader:
        if not db.find(uid):
            db.insert({'_id': uid})

with open('/Users/cchen/Desktop/makeup', 'r') as i:
    db_taobao = MongoDB('wanghong', 'taobao_shops')
    db_users = MongoDB('wanghong', 'users')
    csvreader = csv.reader(i, delimiter=str('\t'))
    for uid, shopid in csvreader:
        db_users.update(uid, {'taobao_shopid': shopid.strip()})
        try:
            db_taobao.insert({'_id': shopid.strip(), 'weibo_id': uid})
        except:
            db_taobao.update(shopid.strip(), {'weibo_id': uid})

db_taobao.insert({'_id': '102955637', 'weibo_id': '1626466994'})


for user_doc in db_users.find_all({'taobao_id': {'$ne': None}, 'taobao_shopid': None}):
    db_users.update(user_doc['_id'], {'taobao_shopid': user_doc['taobao_id']})

db_users = MongoDB('wanghong', 'users')
db_yizhibo = MongoDB('wanghong', 'yizhibo_users')
for users in db_users.find_all({'yizhibo_id': {'$ne': None}}):
    db_yizhibo.insert({'_id': users['yizhibo_id'], 'weibo_id': users['_id']})

db_items = MongoDB('wanghong', 'taobao_items')
uids = {doc['shopid'] for doc in db_items.find_all()}
db_shops = MongoDB('wanghong', 'taobao_shops')
total = {doc['_id'] for doc in db_shops.find_all() if doc['_id']}

len(total - uids)


db_users = MongoDB('yizhibo', 'users')
db_weibousers = MongoDB('yizhibo', 'weibo_users')
docs = [doc for doc in db_weibousers.find_all()]


import random
samples = range(10049999, 331565499)[::-1]
samples = random.sample(samples, len(samples))
# with open('inputs/users')
# [str(item) for item in ]

db_items = MongoDB('yizhibo', 'taobao_items')
docs = {doc['_id'] for doc in db_items.find_all()}


db1 = MongoDB('yizhibo', 'weibo_users')
db2 = MongoDB('yizhibo', 'taobao_shops')

for doc in db1.find_all({'task.shopid_manual.status': 'done',
                         'taobao_shopid': {'$exists': True}}):
    for tid in doc['taobao_shopid'].split(','):
        if not db2.insert({'_id': tid, 'weibo_id': doc['_id']}):
            db2.update(tid, {'_id': tid, 'weibo_id': doc['_id']})

import json
from glob import glob
from pachong.database import MongoDB
db = MongoDB('yizhibo', 'taobao_items')
for fp in glob('/Users/cchen/Downloads/wh/yizhibo_taobaoitems*.json'):
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line)
            db.update(jline['_id'], jline)
docs = [doc['_id'] for doc in db.find_all({'task.comments.status': {'$ne': 'done'}})]


from pachong.database import MongoDB
from glob import glob
from tqdm import trange
import random
minimum = 10049999
maximum = 331565500
step = 100000
db = MongoDB('yizhibo', 'users')
with open('unhave.txt', 'w') as o:
    for x in trange((maximum - minimum) // step + ((maximum - minimum) % step > 0)):
        candidates = [str(item) for item in range(minimum + step * x, minimum + step * (x + 1)) if item < maximum]
        have = {doc['_id'] for doc in db.find_all({'_id': {'$in': candidates}})}
        for item in set(candidates) - have:
            o.write(item + '\n')



# q3 = (maximum - minimum) / 4 * 3

for fp in glob('inputs/users*.txt'):
    with open(fp, 'r') as i:
        for line in i:
            if line.strip():
                try:
                    docs.remove(line.strip())
                except KeyError:
                    continue

# samples -= {doc['_id'] for doc in db.find_all() if int(doc['_id']) >= 10049999}

with open('unhave.txt', 'r') as i:
    docs = [line.strip() for line in i if line.strip()]
import random
from bson import json_util
docs = random.sample(docs, len(docs))
import math
import json
max_file = 18
len_per_file = len(docs) // max_file + (len(docs) % max_file > 0)

for counter, i_file in enumerate(range(max_file)):
    with open('/Users/cchen/Downloads/inputs/itaobao_items{}.json'.format(i_file), 'w') as f:
        [f.write(json.dumps(doc, default=json_util.default) + '\n') for doc in docs[i_file * len_per_file: (i_file + 1) * len_per_file]]


from glob import glob
for counter, fp in enumerate(glob('inputs/users*.txt')):
    with open(fp, 'a') as o, open('inputs2/users{}.txt'.format(counter), 'r') as i:
        for line in i:
            if line.strip():
                o.write(line.strip() + '\n')

db1 = MongoDB('wanghong', 'keyweibos')
db2 = MongoDB('wanghong', 'taobaodianzhu')
for doc in db1.find_all():
    db2.insert(doc['uid'])

db = MongoDB('yizhibo', 'taobao_items')
docs = [doc for doc in db.find_all({'task.comments.datetime': {'$exists': False}})]



zhiboids = {doc['_id'] for doc in MongoDB('yizhibo', 'weibo_users').find_all()}
uids = {doc['uid'] for doc in MongoDB('wanghong', 'keyweibos').find_all() if doc['_id'] not in zhiboids}
db = MongoDB('wanghong', 'taobaodianzhu')
db2 = MongoDB('wanghong', 'users')
for doc in db2.find_all():
    if doc['_id'] not in zhiboids:
        db.update(doc['_id'], doc)


db = MongoDB('yizhibo', 'taobao_items')
from glob import glob
from tqdm import tqdm
import json
for fp in tqdm(glob('/Users/cchen/Downloads/wh/otaobao_items*.json')):
    # count = 0
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line)
            # if jline.get('task', {}).get('chatroom', {}).get('status', '') == 'done':
            #     count += 1
            db.update(jline['_id'], jline)
    # print count
            # if not db.insert(jline):
            #     db.update(jline['_id'], jline)

db_shops = MongoDB('yizhibo', 'taobao_shops')
uids = [doc['weibo_id'] for doc in db_shops.find_all()]
db_weibo = MongoDB('yizhibo', 'weibo_users')
docs = [doc['_id'] for doc in db_weibo.find_all({'_id': {'$in': uids}})]
exclude = set(uids) - set(docs)


with open('/Users/cchen/Dropbox/WangHongSeller/data_v2.csv', 'r') as i:
    csvreader = csv.reader(i)
    next(csvreader)
    shop_uid = {row[1]: row[0] for row in csvreader}
for shop, uid in shop_uid.items():
    db_shops.update(shop, {'weibo_id': uid})

for doc in db_weibo.find_all({'taobao_shopid': {'$exists': True}}):
    try:
        shops = doc['taobao_shopid'].split(',')
        for shop in shops:
            for item in exclude:
                if shop == item:
                    db_shops.update(shop, {'weibo_id': doc['_id']})
                    break
    except:
        pass

    if len(shopcount) == 1 and shopcount.values()[0] >= 5:


import json
import re
out = []
for doc in db_weibo.find_all({'taobao_shopid': {'$exists': True}}):
    item = '157032472'
    if re.compile(item).search(json.dumps(doc)):
        out.append(doc)
db_shops.update('157032472', {'weibo_id': '5483874634'})

from pachong.database import MongoDB
db = MongoDB('yizhibo', 'replays')
docs = [{'_id': doc['_id']} for doc in db.find_all({'task.chatroom.status': {'$ne': 'done'}})]



db_shops = MongoDB('yizhibo', 'taobao_shops')
db_weibo = MongoDB('yizhibo', 'weibo_users')
db_zhibo = MongoDB('yizhibo', 'users')
db_replays = MongoDB('yizhibo', 'replays')

db_replays_tar = MongoDB('yizhibo', 'replays_target')
docs = [doc for doc in db_replays_tar.find_all({'task.chatroom.status': {'$ne': 'done'}})]
for doc in replays:
    db_weibo_tar.insert(doc)

sid_wid = {doc['_id']: doc['weibo_id'] for doc in db_shops.find_all()}
wids = list(set(sid_wid.values()))
weibo_users = [doc for doc in db_weibo.find_all({'_id': {'$in': wids}})]
zhibo_users = [doc for doc in db_zhibo.find_all({'weibo_openid': {'$in': wids}})]
wid_yid = {doc['weibo_openid']: doc['_id'] for doc in zhibo_users}
wid_weibousers = {doc['_id']: doc for doc in weibo_users}
replays = [doc for doc in db_replays.find_all({'uid': {'$in': wid_yid.values()}})]


import csv
with open('/Users/cchen/Dropbox/WangHongSeller/shops.csv', 'w') as o:
    csvwriter = csv.writer(o)
    csvwriter.writerow(['shop_id', 'weibo_id', 'yizhibo_id', 'weibo_nick', 'birthday', 'gender',
                        'n_weibos', 'n_followers', 'n_followings', 'location'])
    for sid, wid in sid_wid.items():
        yid = wid_yid.get(wid)
        weibouser = wid_weibousers.get(wid)
        if yid and weibouser:
            row = [sid, wid, yid,
                   weibouser.get('nick', '').encode('utf-8'),
                   weibouser.get('birthday', '').encode('utf-8'),
                   weibouser.get('gender', '').encode('utf-8'),
                   weibouser.get('n_weibos', 0),
                   weibouser.get('n_followers', 0),
                   weibouser.get('n_followings', 0),
                   weibouser.get('location', '').encode('utf-8')]
            csvwriter.writerow(row)



db = MongoDB('yizhibo', 'replays_target')
docs = [doc for doc in db.find_all({'task.comments.status': {'$ne': 'done'}})]


db1 = MongoDB('yizhibo', 'users_target')
db2 = MongoDB('yizhibo', 'weibo_users_target')
for doc in db1.find_all():
    db2.update(doc['weibo_openid'], {'yizhibo_id': doc['_id']})

db = MongoDB('yizhibo', 'taobao_items')
docs = [doc for doc in db.find_all({'price': None, 'task.comments.other': {'$ne': 'TargetNoLongerAvailable'}})]

db= MongoDB('yizhibo', 'users_target')
db_replays =  MongoDB('yizhibo', 'replays_target')
db_shops = MongoDB('yizhibo', 'taobao_shops')
weiboids = [doc['weibo_id'] for doc in db_shops.find_all()]
users = [doc for doc in MongoDB('yizhibo', 'users').find_all({'weibo_openid': {'$in': weiboids}})]
uids = [user['_id'] for user in users]



docs = [doc for doc in db.find_all()]
uids = {doc['uid'] for doc in db_replays.find_all()}
firststreams = [d for d in db_replays.find_all({'_id': {'$in': [doc['firststream']['roomid'] for doc in docs]}})]

docs = [doc for doc in db_replays.find_all({'task.comments.status': {'$ne': 'done'}})]

from glob import glob
db = MongoDB('yizhibo', 'comments')
db_c = MongoDB('yizhibo', 'taobao_comments')
for doc in db.find_all({'bidPriceMoney': {'$exists': True}}):
    if not db_c.insert(doc):
        db_c.update(doc['_id'], doc)
    db.drop(doc['_id'])


db = MongoDB('wanghong', 'taobao_items')
for fp in glob('/Users/cchen/Downloads/wh2/otaobao_items*.json'):
    with open(fp, 'r') as i:
        for line in i:
            jline = json.loads(line)
            db.update(jline['_id'], jline)

from datetime import datetime
db = MongoDB('yizhibo', 'taobao_items')
for doc in db.find_all():
    doc['task']['comments']['datetime'] = datetime.strptime(doc.get('task', {}).get('comments', {}).get('datetime'), '%Y-%m-%d_%H:%M:%S')
    db.update(doc['_id'], doc)


docs = [doc for doc in db.find_all()]



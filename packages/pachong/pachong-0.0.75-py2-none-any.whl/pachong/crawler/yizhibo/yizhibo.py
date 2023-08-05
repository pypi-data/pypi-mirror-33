#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/4/18
# @File  : [pachong] yizhibo.py



from __future__ import absolute_import
from __future__ import unicode_literals

from tqdm import tqdm

from .parsers import parse_chatroom
from .parsers import parse_chatroom_user
from .parsers import parse_comments
from .parsers import parse_profile
from .parsers import parse_replaylist
from ..pachong import Pachong
from ...fetcher import Browser
from ...fetcher import Requests


class Yizhibo(Pachong):
    tasks_available = {
        'yizhibo_from_weibo': Browser,
        'profile': Requests,
        'replaylist': Requests,
        'chatroom': Requests,
        'comments': Requests,
    }

    def profile(self, target):
        uid = target['_id']
        self.fetcher.get('https://www.yizhibo.com/member/personel/user_info',
                         params={'memberid': uid, 'jumpbrowser': 1})
        chong = parse_profile(self.fetcher)
        if chong:
            chong['_id'] = uid
            yield chong

    def replaylist(self, target):
        uid = target['_id']
        self.fetcher.get('https://www.yizhibo.com/member/personel/user_works',
                         params={'memberid': uid})
        for chong in parse_replaylist(self.fetcher):
            chong['uid'] = uid
            yield chong

    def chatroom(self, target):
        roomid = target['_id']
        self.fetcher.get('https://www.yizhibo.com/l/{}.html'.format(roomid))
        chong = parse_chatroom(self.fetcher)
        if chong:
            yield chong

    def room(self, target):
        roomid = target['_id']
        self.fetcher.get('https://www.yizhibo.com/l/{}.html'.format(roomid))
        chong = parse_chatroom_user(self.fetcher)
        if chong:
            chong['_id'] = target['uid']
            yield chong

    def comments(self, target):
        roomid = target['_id']
        minimum = target.get('play', {}).get('length') / 3 + 1
        count = 0
        with tqdm() as bar:
            while True:
                self.fetcher.get('https://www.yizhibo.com/live/h5api/get_playback_event',
                                 params={'scid': roomid, 'ts': str(int(str(count * 3) + str(count).zfill(4)))})
                chongs = parse_comments(self.fetcher)
                for chong in chongs:
                    chong['_id'] = chong.pop('id')
                    chong['replayid'] = roomid
                    yield chong
                if count > minimum and len(chongs) == 0:
                    break
                count += 1
                bar.update(1)

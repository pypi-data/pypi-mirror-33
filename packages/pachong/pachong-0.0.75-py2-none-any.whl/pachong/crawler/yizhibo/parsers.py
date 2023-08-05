#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/5/18
# @File  : [pachong] parsers.py

from __future__ import absolute_import
from __future__ import unicode_literals

import re
from datetime import datetime
from datetime import timedelta
from ..common.exceptions import TaskDoneOther

import json
from pachong.crawler.common.utils import keep_int
from pachong.crawler.common.utils import keep_float


def parse_profile(fetcher, attributes='nick,avatar,pinfo,level,n_followers,n_fans'):
    if fetcher.find('img', class_='icon_404'):
        return None
    chong = {}
    profile = fetcher.find('div', class_='person_info')
    if 'nick' in attributes:
        nick = profile.find('div', class_='person_name')
        if nick:
            chong['nick'] = nick.get_text(strip=True)
    if 'avatar' in attributes:
        avatar = profile.find('div', class_='person_header').find('img')
        if avatar:
            chong['avatar'] = re.sub('@[^@]+\.jpg$', '',avatar.get('src', ''))
    if 'pinfo' in attributes:
        pinfo = profile.find('div', class_='person_intro')
        if pinfo:
            chong['pinfo'] = pinfo.get_text(strip=True, separator=u' ')
    if 'level' in attributes:
        level = profile.find('div', class_=re.compile('level_[0-9]+'))
        if level:
            chong['level'] = int(re.compile('level_([0-9]+)').search(' '.join(level.get('class', []))).group(1))

    social = fetcher.find('div', class_='person_concern')
    if 'n_followers' in attributes:
        n_followers = social.find('div', class_='concern_num')
        if n_followers:
            chong['n_followers'] = int(n_followers.find('span').get_text(strip=True))
    if 'n_fans' in attributes:
        n_fans = social.find('div', class_='fan_num')
        if n_fans:
            chong['n_followers'] = int(n_fans.find('span').get_text(strip=True))
    return chong


def parse_replaylist(fetcher, attributes='n_views,date,title,n_likes,n_messages,cover'):
    if fetcher.find('img', class_='icon_404'):
        return None
    rooms = fetcher.find_all('li', class_='index_all_common')
    return [_parse_replay(room, attributes) for room in rooms]


def _parse_replay(room, attributes):
    chong = {}
    chong['_id'] = room.find('div', class_='scid').text
    if '照片' in room.find('div', class_='index_time').text:
        chong['type'] = 'photo'
    else:
        status = room.find('div', class_='index_state').get_text(strip=True)
        chong['type'] = 'replay' if '回放' in status else 'live'

    if 'n_views' in attributes:
        n_views = room.find('div', class_='index_num')
        if n_views:
            chong['n_views'] = keep_int(n_views.text)
    if 'date' in attributes:
        date = room.find('div', class_='index_time')
        if date:
            date_text = date.text
            chong['date'] = (datetime.utcnow() + timedelta(hours=8) -
                             (timedelta(hours=keep_int(date_text)) if '小时' in date.text else
                              timedelta(minutes=keep_int(date_text)))).strftime('%Y-%m-%d') \
                if '前' in date_text else re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}').search(date_text).group(0)
    if 'title' in attributes:
        title = room.find('div', class_='index_intro')
        if title:
            chong['title'] = title.get_text(strip=True)
    if 'n_likes' in attributes:
        n_likes = room.find('div', class_='index_zan')
        if n_likes:
            chong['n_likes'] = keep_int(n_likes.text)
    if 'n_messages' in attributes:
        n_messages = room.find('div', class_='index_msg')
        if n_messages:
            chong['n_messages'] = keep_int(n_messages.text)
    if 'cover' in attributes:
        cover = room.find('img', class_='index_img_main')
        if cover:
            chong['cover'] = re.sub('@.+$' , '', cover.get('src', ''))
    return chong


def parse_chatroom(fetcher):
    if fetcher.find('script', text=re.compile('该视频无法播放，点击确定观看主播最新回放')):
        raise TaskDoneOther('TargetNoLongerAvailable')

    script = fetcher.find('script', type='text/javascript').text
    script = re.sub(';', '', script)
    script = re.sub('\n +([^ :]+):', '"\\1":', script)
    script = re.compile('{[^{}]+}').search(script).group(0)
    window_anchor = eval(script)

    chong = {}
    chong['starttime'] = window_anchor['starttime']
    chong['stat_hits'] = keep_int(window_anchor['stat_hits'])
    chong['play.url'] = window_anchor['play_url']

    fetcher.get(window_anchor['play_url'])
    play_info = fetcher.source_code()
    play_segs = [keep_float(line.split(':')[-1]) for line in play_info.splitlines() if line.startswith('#EXTINF:')]
    chong['play.segments'] = len(play_segs)
    chong['play.length'] = sum(play_segs)
    return chong


def parse_chatroom_user(fetcher, attributes='store,weibo_openid,goldcoin,n_followers'):
    timenow = datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S')
    script = fetcher.find('script', type='text/javascript').text
    script = re.sub(';', '', script)
    script = re.sub('\n +([^ :]+):', '"\\1":', script)
    script = re.compile('{[^{}]+}').search(script).group(0)
    window_anchor = eval(script)

    attributes = set(attributes.split(','))
    chong = {}
    if 'store' in attributes:
        store = fetcher.find('div', class_='mystore')
        if store:
            chong['store'] = {}
            url = store.find('a', text='进入小店')
            if url:
                chong['store']['url'] = url.get('href', '')
            items = store.find_all('a', class_='J_p_from')
            if items:
                chong['store']['items'] = [item_url.get('href', '') for item_url in items]
    if 'weibo_openid' in attributes:
        avatar = fetcher.find('div', class_=re.compile('avatar'))
        if avatar:
            weibo_openid = avatar.find('a').get('weibo_openid')
            if weibo_openid:
                chong['weibo_openid'] = weibo_openid
    if 'goldcoin' in attributes:
        if 'goldcoin' in window_anchor:
            chong['goldcoin'] = window_anchor['goldcoin']
            chong['track.{}.goldcoin'.format(timenow)] = window_anchor['goldcoin']
    if 'n_followers' in attributes:
        if 'follow_count' in window_anchor:
            chong['n_followers'] = window_anchor['follow_count']
            chong['track.{}.n_followers'.format(timenow)] = window_anchor['follow_count']
    return chong


def parse_comments(fetcher):
    return json.loads(fetcher.soup.text)['data']['list']

# def parse_usercard(usercard):
#     link = usercard.find('a', target='_blank')
#     memberid = parse_url_args(link.attrs['href'])['memberid']
#     weiboid = link.attrs.get('weibo_openid', '')
#     nickname = link.text.encode('utf-8')
#     level = re.sub('[^0-9]', '', ' '.join(usercard.find('div', class_='level').attrs['class']))
#
#     gold = usercard.find('span', class_='J_goldcoin')
#     gold = gold.text.encode('utf-8') if gold else ''
#     maxonline = usercard.find('span', class_='J_maxonline')
#     maxonline = re.sub(u'\u4eba', '', maxonline.text).encode('utf-8') if maxonline else ''
#
#     return [memberid, weiboid, nickname, level, gold, maxonline]

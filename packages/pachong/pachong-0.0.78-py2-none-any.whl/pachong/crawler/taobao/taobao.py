#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/27/18
# @File  : [pachong] taobao.py


from __future__ import division
from __future__ import unicode_literals

import math
import random
import re
import time
from datetime import datetime

from future.builtins import input
from pushbullet import PushBullet
from tqdm import tqdm
from tqdm import trange

from .parsers import is_available
from .parsers import parse_comment_pages
from .parsers import parse_comments
from .parsers import parse_item
from .parsers import parse_itempage
from .parsers import parse_shop_main
from .parsers import parse_shop_rate
from .parsers import parse_shop_urls
from .parsers import parse_shopid_from_itempage
from ..pachong import Pachong
from ...fetcher import Browser
from ...fetcher import Requests


class Taobao(Pachong):

    tasks_available = {
        'shop': (Requests, Browser),
        'itemlist': Browser,
        'shopid_from_weibostore': Requests,
        'itempage': Browser,
        'comments': Browser,
    }

    def login(self, username=None, password=None):
        if not username and not password:
            self.fetcher.get('https://login.taobao.com/')
            input('press any after manually logged in.')
            return self
        self.fetcher.get('https://world.taobao.com/markets/all/login')
        self.fetcher.session.switch_to_frame('login-iframe')
        self.fetcher.find('input', name='TPL_username').send_keys(username)
        self.fetcher.find('input', name='TPL_password').send_keys(password)
        self.fetcher.find('button', id='submit').submit()
        while True:
            if 'login' not in self.fetcher.session.current_url:
                break
            self.logger.push('LOGIN', 'Please manually finish verification.')
            time.sleep(30)
            return self

    def captcha_handler(self):
        if re.compile('sec\.taobao').search(self.fetcher.current_url):
            verfication_code = input(self.fetcher.find('img', id='J_CheckCodeImg').get_attribute('src'))

        self.fetcher.session.switch_to_default_content()
        iframe = self.fetcher.find('iframe', id='sufei-dialog-content')
        if iframe:
            self.fetcher.session.switch_to_frame(iframe)
            if self.fetcher.find('div', id='J_LoginBox'):
                self.login()
            elif self.fetcher.find('div', id='J_CodeContainer'):
                input_field = self.fetcher.find('input', type='text', id='J_CodeInput')
                while self.fetcher.find('button', id='J_submit'):
                    input_field.clear()
                    verfication_code = input(self.fetcher.find('img', id='J_CheckCodeImg1').get_attribute('src'))
                    # response = self.pb.push_link('淘宝验证', self.fetcher.find('img', id='J_CheckCodeImg1')
                    # .get_attribute('src'))
                    # receive = False
                    # while not receive:
                    #     time.sleep(60)
                    #     pushes = self.pb.get_pushes()
                    #     if pushes[1]['iden'] == response['iden']:
                    #         verfication_code = pushes[0]['body'].strip()
                    #         receive = True
                    input_field.send_keys(verfication_code)
                    self.fetcher.find('button', id='J_submit').click()
                    time.sleep(15)
            self.fetcher.session.switch_to_default_content()

    def shop(self, target):
        # if self.input_ is self.output:
        self.fetcher.get('https://shop{}.taobao.com/'.format(target['_id']),
                         sleep=random.random() * 5 + 5)
        self.captcha_handler()
        shop_url, rate_url = parse_shop_urls(self.fetcher)
        self.fetcher.get(shop_url, sleep=random.random() * 5 + 5)
        self.captcha_handler()
        chong = parse_shop_main(self.fetcher)
        self.fetcher.get(rate_url, sleep=random.random() * 5 + 5)
        self.captcha_handler()
        chong.update(parse_shop_rate(self.fetcher))
        yield chong

    def itemlist(self, target):
        page = target.get('task', {}).get('itemlist', {}).get('page', 1)
        self.fetcher.get('https://shop{}.taobao.com/search.htm'.format(target['_id']))

        if not is_available(self.fetcher, '没有找到相应的店铺信息') or \
                'guang.taobao.com' in self.fetcher.session.current_url or \
                self.fetcher.find('strong', text=re.compile('很抱歉，搜索到')):
            raise StopIteration

        if page != 1:
            self.captcha_handler()
            page_number = self.fetcher.find('input', name='pageNo')
            page_number.clear()
            page_number.send_keys('{}'.format(int(page)))
            page_number.submit()
            time.sleep(5)

        _next = True
        while _next:
            self.captcha_handler()
            next_btn = self.fetcher.wait_until(lambda x: x.find_element_by_link_text('下一页'))
            search_result = self.fetcher.find('div', id='J_ShopSearchResult')
            search_feeds = search_result.find_all('dl', class_=re.compile('item'))
            # search_result.find_elements_by_xpath('//dl[@data-id and contains(@class, "item ")]')
            for item in search_feeds:
                chong = parse_item(item)
                chong['shopid'] = target['_id']
                yield chong
            self.input_.update(target['_id'], {'task.itemlist.page': page})
            if next_btn:
                if next_btn.get_attribute('class') == 'disable':
                    _next = False
                else:
                    next_btn.click()
                    page += 1
                    time.sleep(10)
            else:
                raise LookupError('Next page button not found.')

    def itempage(self, target):
        self.fetcher.get('https://item.taobao.com/item.htm', params={'id': target['_id']},
                         until_not=lambda x: x.find_element_by_xpath(
                             '//div[@id="J_DivItemDesc" and contains(text(), "描述加载中")]'))

        if self.fetcher.find('iframe', id='sufei-dialog-content'):
            self.fetcher.find('div', id='sufei-dialog-close').click()

        chong = parse_itempage(self.fetcher)
        if chong:
            chong['_id'] = target['_id']
            yield chong

    def comments(self, target):
        self.fetcher.get('https://item.taobao.com/item.htm', params={'id': target['_id']})
        if self.fetcher.find('iframe', id='sufei-dialog-content'):
            self.fetcher.find('div', id='sufei-dialog-close').click()
        # self.captcha_handler()

        iteminfo = parse_itempage(self.fetcher)
        self.fetcher.proxy.new_har()
        self.fetcher.find('a', {'shortcut-label': '查看累计评论'}).click()
        comments = parse_itempage(self.fetcher, attributes='comments')
        iteminfo['comments'] = comments['comments']
        iteminfo[[key for key in iteminfo.keys() if key.startswith('n_comments')][0]] = comments['comments']
        self.input_.update(target['_id'], iteminfo)
        if not max(iteminfo.get('comments', 0), target.get('comments', 0)):
            raise StopIteration

        unfolded_urls, folded_urls = parse_comment_pages(self.fetcher)
        ua_containers = [re.compile('ua=([^&]+)').search(url).group(1) for url in unfolded_urls]
        if unfolded_urls:
            with tqdm(unfolded_urls, desc='unfolded') as bar:
                for url in bar:
                    self.fetcher.get(url)
                    total, chongs = parse_comments(self.fetcher)
                    for chong in chongs:
                        chong['_id'] = str(chong.pop('rateId'))
                        chong['itemid'] = target['_id']
                        yield chong

        if folded_urls:
            folded_url = folded_urls[0]
            self.fetcher.get(folded_url)
            total, chongs = parse_comments(self.fetcher)

            if total:
                total_page = int(math.ceil(total / 20))
                with trange(1, total_page + 1, desc='folded') as bar:
                    for page in bar:
                        folded_url = re.sub('currentPageNum=[0-9]+',
                                            'currentPageNum={}'.format(page),
                                            folded_url)
                        folded_url = re.sub('pageSize=[0-9]+',
                                            'pageSize=20',
                                            folded_url)
                        folded_url = re.sub('_ksTS=([0-9]{13})_([0-9]+)',
                                            # lambda x: '_ksTS={}_{}'.format(x.group(1), self.guid(x.group(2), inc=13)),
                                            lambda x: '_ksTS={}_{}'.format(self.utc_now(), int(x.group(2)) + 13),
                                            folded_url)
                        folded_url = re.sub('ua=([^&]+)',
                                            'ua={}'.format(random.sample(ua_containers, 1)[0]),
                                            folded_url)
                        self.fetcher.get(folded_url, sleep=random.random())
                        total, chongs = parse_comments(self.fetcher)
                        for chong in chongs:
                            chong['_id'] = str(chong.pop('rateId'))
                            chong['itemid'] = target['_id']
                            yield chong

    def shopid_from_weibostore(self, target):
        # if target.get('task', {}).get('shopid_manual', {}).get('status') != 'done':
            shopids = dict()
            with tqdm(target.get('store', {}).get('urls', [])) as items:
                for item_url in items:
                    self.fetcher.get(item_url)
                    shopid = parse_shopid_from_itempage(self.fetcher)
                    if shopid:
                        if shopid in shopids:
                            shopids[shopid] += 1
                        else:
                            shopids[shopid] = 1
            # drop = []
            # for k, v in shopids.items():
            #     if v == 1:
            #         drop.append(k)
            # for k in drop:
            #     shopids.pop(k)
            if '0' in shopids:
                shopids.pop('0')
            if len(shopids) >= 1:
                yield {'store.taobao_shopcount': shopids}
            # if len(shopids) > 1:
            #     yield
            # elif len(shopids) == 1:
            #     yield {'taobao_shopid': shopids.keys()[0]}

    def set_pushbullet(self, token):
        self.pb = PushBullet(token)
        return self

    @staticmethod
    def utc_now():
        return '{:13d}'.format(int((datetime.now() - datetime(1970, 1, 1)).total_seconds() * 1000))

    @staticmethod
    def guid(guid, inc=13, digit=4):
        return '{:' + str(len(str(guid))) + 'd}'.format(
            int(guid) + inc) if guid else int(random.random() * (10 ** digit))

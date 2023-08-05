#-*-coding:utf-8-*-
__author__ = 'cchen'

import json
import random
import re
import time
import traceback
from urlparse import urljoin

from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from tqdm import tqdm

from pachong import PaChong
from weibo_login import WeiboLogin
from weibo_parsers import parse_weibostore, parse_weibo


class Weibo(PaChong):

    def login(self, username, password):
        self.session = WeiboLogin(self.session).login(username, password)

    def streaming(self, fp_timeline, fp_uids, period=30):
        whatwehave = self.read_records(fp_timeline, col_id=(0, 1))
        trgt_users = self.read_records(fp_uids, col_id=1) if not isinstance(fp_uids, (set, list)) else set(fp_uids)

        while True:
            new_weibos = []
            for uid in trgt_users:
                has_next, weibos, page_property = self._crawl_timeline_feed(uid, page=1, pagebar=-1)
                for weibo in weibos:
                    uid_mid = weibo[0] + '_' + weibo[1]
                    if uid_mid in whatwehave:
                        continue
                    new_weibos.append(weibo)
                    whatwehave.add(uid_mid)
            self.write_records(new_weibos, fp_timeline, log=u'微博')
            self.hibernate(period)

    def _crawl_profile(self, uid):
        soup = self.get_soup('https://weibo.com/{}'.format(uid))

        profile_wrap = self.retrieve_script(
            soup.find('script', text=re.compile('"domid": *"Pl_Core_UserInfo__[0-9]"')).text)
        profile_html = json.loads(profile_wrap)['html']
        profile_soup = BeautifulSoup(profile_html, 'lxml')
        is_bigV = 1 if profile_soup.find('a', class_='icon_verify_v') else 0
        level_soup = profile_soup.find('a', class_='W_icon_level')
        level = int(re.compile('Lv\.([0-9]+)').search(level_soup.get_text(strip=True)).group(1))
        winfo_soup = profile_soup.find('p', class_='info')
        winfo = winfo_soup.get_text(strip=True).encode('utf-8') \
            if winfo_soup else ''
        place_soup = profile_soup.find('em', class_='ficon_cd_place')
        place = place_soup.find_next('span').get_text(strip=True).encode('utf-8') \
            if place_soup else ''
        edu_soup = profile_soup.find('em', class_='ficon_edu')
        edu = re.sub(u'毕业于', u'', edu_soup.find_next('span').get_text(strip=True)).encode('utf-8') \
            if edu_soup else ''
        birthday_soup = profile_soup.find('em', class_='ficon_constellation')
        birthday = birthday_soup.find_next('span').get_text(strip=True).encode('utf-8') \
            if birthday_soup else ''
        pinfo_soup = profile_soup.find('em', class_='ficon_pinfo')
        pinfo = re.sub(u'简介：[ \t]*', u'', pinfo_soup.find_next('span').get_text(strip=True)).encode('utf-8') \
            if pinfo_soup else ''
        baidu_card_soup = profile_soup.find('i', class_='pinfo_icon_baidu')
        baidu_card = baidu_card_soup.find_next('a').get('href') \
            if baidu_card_soup else ''

        social_wrap = self.retrieve_script(
            soup.find('script', text=re.compile('"domid": *"Pl_Core_T8CustomTriColumn__3"')).text)
        social_html = json.loads(social_wrap)['html']
        social_soup = BeautifulSoup(social_html, 'lxml')
        n_following_soup = social_soup.find('a', href=re.compile('mod=headfollow'))
        n_following = n_following_soup.strong.text if n_following_soup else '0'
        n_followers_soup = social_soup.find('a', href=re.compile('mod=headfans'))
        n_followers = n_followers_soup.strong.text if n_followers_soup else '0'
        n_weibos_soup = social_soup.find('a', href=re.compile('mod=data'))
        n_weibos = n_weibos_soup.strong.text if n_weibos_soup else '0'

        page_property = self.get_page_property(
            soup.find('script', type='text/javascript', text=re.compile('\\$CONFIG')).get_text(strip=True),
            var_name='$CONFIG')
        page_id = page_property['page_id']

        return [page_id, n_following, n_followers, n_weibos,
                is_bigV, level, winfo,
                place, edu, birthday, pinfo, baidu_card,]

    def crawl_timeline(self, fp_timeline, fp_uids, sample_size=0):
        targt_uids = self.read_records(fp_uids, col_id=1) if not isinstance(fp_uids, (set, list)) else set(fp_uids)
        saved_uids = self.read_records(fp_timeline, col_id=0)
        error_uids = self.read_records('zhuliren_timeline.err', 0)
        print len(targt_uids)
        print len(saved_uids)
        print len(error_uids)
        uids = targt_uids - saved_uids - error_uids
        print len(uids)
        with tqdm(random.sample(uids, len(uids) if sample_size==0 else sample_size)) as bar:
            for uid in bar:
                try:
                    page = 1
                    wbs = []
                    while True:
                        self.logger.info(uid + ': page' + str(page))
                        has_next, wb_c = self._crawl_timeline(uid, page)
                        page += 1
                        if not has_next:
                            break
                        wbs += wb_c
                    self.write_records(wbs, fp_timeline)
                    self.logger.info(uid + ': records wrote.')
                    bar.set_description(uid + ' page' + str(page))
                except ConnectionError:
                    self.logger.info(uid + ': connection error.')
                    pass
                except KeyboardInterrupt:
                    break
                except Exception, e:
                    with open('zhuliren_timeline.err', 'a') as oe:
                        oe.write(uid + '\n')
                    self.logger.info(uid + ': other error.\n{}'.format(traceback.print_exc()))

    def _crawl_timeline_feed(self, uid, page, pagebar, page_property=None):
        params = {
            'is_search': '0',
            'visible': '0',
            'is_all': '1',
            'is_tag': '0',
            'profile_ftype': '1',
            'page': page,
        }

        if pagebar != -1:
            params.update({
                'ajwvr': '6',
                'domain': page_property['domain'],
                'pl_name': 'Pl_Official_MyProfileFeed__23',
                'id': page_property['page_id'],
                'script_uri': '/' + page_property['oid'],
                'feed_type': '0',
                'pagebar': pagebar,
                'pre_page': page,
                'domain_op': page_property['domain'],
                '__rnd': int(self.utc_now() * 1000)
            })
        if pagebar == -1:
            soup = self.get_soup('https://weibo.com/{}'.format(uid), params=params)
            feed = soup.find('script',
                             text=lambda x: self.json_has(self.parse_script(x, within='FM\\.view\((.*)\)'),
                                                          attrs={'ns': 'pl.content.homeFeed.index',
                                                                 'domid': re.compile('MyProfileFeed')}))
            if not feed:
                with open('error.html', 'w') as o:
                    o.write(soup.prettify().encode('utf-8'))
                raise LookupError('cao')
            feed_html = self.parse_script(feed.text, within='FM\\.view\((.*)\)')
            feed_soup = BeautifulSoup(feed_html['html'], 'lxml')

            if page_property is None:
                page_property = self.get_page_property(
                    soup.find('script', type='text/javascript', text=re.compile('\\$CONFIG')).get_text(strip=True),
                    var_name='$CONFIG')
        else:
            feed_html = self.get_json('http://weibo.com/p/aj/v6/mblog/mbloglist', params=params)
            feed_soup = BeautifulSoup(feed_html['data'], 'lxml')
        feed_list = feed_soup.find_all('div', attrs={'class': 'WB_cardwrap', 'action-type': 'feed_list_item'})
        has_next = True if feed_list else False

        weibos = []
        for weibo in feed_list:
            record = parse_weibo(weibo, target_uid=uid)
            if record:
                weibos.append(record)
        if len(weibos) < 15:
            has_next = False
        return has_next, weibos, page_property

    def _crawl_timeline(self, uid, page=1):
        weibos = []
        page_property = None
        has_next = True
        for pagebar in xrange(-1, 2):
            has_next, feeds, page_property = self._crawl_timeline_feed(uid, page, pagebar, page_property=page_property)
            weibos += feeds
        return has_next, weibos

    def crawl_weibostores(self, fp_userlist, fp_goodlist, fp_emptycache):
        targt_users = self.read_records(fp_userlist, col_id=1)
        saved_users = self.read_records(fp_goodlist)
        empty_users = self.read_list(fp_emptycache)

        print u'开始获取微博橱窗.',
        print u'网址: https://shop.sc.weibo.com/h5/shop/index?weiboUid={}'
        print u'总用户数量: {}, 已获取: {}'.format(len(targt_users), len(saved_users) + len(empty_users))

        for weibo_uid in targt_users - saved_users - empty_users:
            items = self.crawl_weibostore(weibo_uid)
            if items:
                self.write_records(items, fp_goodlist, log=u'商品', log_prefix=u'用户')
            else:
                self.write_line(weibo_uid, fp_emptycache)

    def crawl_weibostore(self, uid):
        page = 0
        store_goods = []
        while True:
            page += 1
            goods = self._crawl_weibostore(uid, page)
            if not goods:
                break
            store_goods += goods
        time.sleep(random.uniform(3, 10))
        return [uid] + store_goods if store_goods else []

    def _crawl_weibostore(self, uid, page=1):
        store_params = {'weiboUid': uid, '__rnd': int(self.utc_now() * 1000)} \
            if page==1 else {'weiboUid': uid, 'page': page, 'shopId': ''}
        store_url = urljoin('https://shop.sc.weibo.com/aj/h5/shop/', 'index' if page==1 else 'recvlist')
        store_html = self.session.get(store_url, params=store_params)
        store_json = json.loads(store_html.content)
        return parse_weibostore(store_json)

    @staticmethod
    def retrieve_script(script):
        return re.compile('FM\\.view\((.*)\)').search(script).group(1)

    @staticmethod
    def is_loggedin(soup):
        return False if 'sina visitor system' in soup.head.get_text(strip=True).lower() else True




# import csv
# from tqdm import tqdm
self = Weibo()
# self.login('0012028475117', 'Cc19900201')
# # self.session.headers.update(
# #     {'Cookie': '_s_tentry=-; Apache=3013807277323.8677.1515737536242; SINAGLOBAL=3013807277323.8677.1515737536242; ULV=1515737536288:1:1:1:3013807277323.8677.1515737536242:; SWBSSL=usrmdinst_0; SCF=Aovj-pOOQZt4zLBttzfKR6UyoBom_t2O7zQ8KolFJPoF94czJAOLjJcbwWgu6E-Jwxth1djgKmqJ98adu3AlOVE.; SUB=_2A253XCG2DeRhGeNG7lUU8S7IwjmIHXVUKBR-rDV8PUNbmtBeLUbQkW9NS1UoyRh2IfKEKVwizot_XZFHyTLrc7k1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWh1ELH-qnd9sSMLfrbakOB5JpX5K2hUgL.Fo-RSKMfeK5X1K-2dJLoIEXLxKnL1K.LB-zLxKqLBoBL1--LxKqL12-LBKzLxKMLBoBLBKzLxKnL1h5L1h-t; SUHB=02MvLLFWnKJr9K; ALF=1516342372; SSOLoginState=1515737574; un=cchenapp@gmail.com; wvr=6; SWB=usrmdinst_14'})
# # crawler.crawl_timeline('test.tsv', '/Users/cchen/GoogleDrive/porkspace/projects/wanghong/wanghongdata/wanghon_weibo.txt')
# pids = self.read_records('/Users/cchen/GoogleDrive/porkspace/packages/pachong2/weibozhuliren_profile_.tsv', 1)
# tars = self.read_records('/Users/cchen/GoogleDrive/porkspace/packages/pachong2/weibozhuliren_profile.err2', 0)
# tars -= pids
# with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong2/weibozhuliren.tsv', 'r') as i, \
#         open('/Users/cchen/GoogleDrive/porkspace/packages/pachong2/weibozhuliren_profile_.tsv', 'a') as o, \
#         open('/Users/cchen/GoogleDrive/porkspace/packages/pachong2/weibozhuliren_profile.err3', 'w') as oe:
#     csvreader = csv.reader(i, delimiter='\t')
#     csvwriter = csv.writer(o, delimiter='\t')
#     for row in tqdm(csvreader):
#         uid = row[1]
#         if uid in tars:
#             try:
#                 row.extend(self._crawl_profile(uid))
#                 csvwriter.writerow(row)
#             except:
#                 oe.write(uid + '\n')
#                 continue
#
# with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong2/weibozhuliren_profile__.tsv', 'r') as i, \
#         open('/Users/cchen/GoogleDrive/porkspace/packages/pachong2/weibozhuliren_profile___.tsv', 'w') as o:
#     csvreader = csv.reader(i, delimiter='\t')
#     csvwriter = csv.writer(o, delimiter='\t')
#     pids = set()
#     lds = set()
#     for row in csvreader:
#         if row[4] and row[5]:
#             ld = '|'.join(row[4:6])
#             if row[1] not in pids and ld not in lds:
#                 csvwriter.writerow(row)
#                 pids.add(row[1])
#                 lds.add(ld)
#         else:
#             if row[1] not in pids:
#                 csvwriter.writerow(row)
#                 pids.add(row[1])
# params = {'profile_ftype': '1',
#           'is_all': '1',
#           'is_search': '1',
#           'key_word': u'一直播#_0'}
#
# soup = self.get_soup('https://weibo.com/p/{}/home'.format(uid), params=params)
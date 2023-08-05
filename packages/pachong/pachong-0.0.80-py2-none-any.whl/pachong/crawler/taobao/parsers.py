#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/28/18
# @File  : [pachong] parsers.py


from __future__ import division
from __future__ import unicode_literals

import json
import re
import time
from datetime import datetime

from bs4 import BeautifulSoup

from ..common.exceptions import TaskDoneOther
from ..common.utils import keep_float
from ..common.utils import keep_int


def parse_shop_urls(fetcher):
    if 'guang.taobao.com' in fetcher.current_url or not is_available(fetcher, '没有找到相应的店铺信息'):
        raise TaskDoneOther('TargetNoLongerAvailable')

    shop_url = fetcher.wait_until(
        lambda x: x.find_element_by_partial_link_text('进入店铺')) \
        .get_attribute('href')
    rate_url = fetcher.wait_until(
        lambda x: x.find('a', href=re.compile('user-rate'))) \
        .get_attribute('href')
    return shop_url, rate_url


def parse_shop_main(fetcher):
    chong = dict()
    page_property = fetcher.find('script', text=re.compile('shop_config'))
    if not page_property:
        raise LookupError('Page property is not found.')
    shop_config = re.compile('window\.shop_config = ({[^;]+});').search(page_property.get_text())
    if not shop_config:
        raise LookupError('Shop configuration is not found.')
    config = json.loads(shop_config.group(1))
    chong['_id'] = config['shopId']
    chong['seller_id'] = config['userId']
    chong['category_id'] = config['shopCategoryId']
    soup = BeautifulSoup(fetcher.session.page_source, 'lxml')
    since = soup.find('span', class_=re.compile('J_id_time'))
    if since:
        chong['since'] = since.get_text()
    name = soup.find('div', class_='hd-shop-name')
    if name:
        chong['shopname'] = name.get_text(strip=True)

    # chong['widgetid'] = fetcher.find('div', class_='J_TLayout').attrs['data-widgetid']
    return chong


def parse_shop_rate(fetcher):
    soup = fetcher.build_soup()

    chong = {}
    ifashion = soup.find('img', src=re.compile('TB1W_vlJFXXXXXxXXXXXXXXXXXX-150-45\.png'))
    if ifashion:
        chong['ifashion'] = 1
    category = soup.find(lambda tag: tag.name=='li' and re.compile('当前主营').search(tag.text))
    if category:
        chong['category'] = category.find('a').text.strip()
    location = soup.find(lambda tag: tag.name == 'li' and re.compile('所在地区').search(tag.text))
    if location:
        chong['location'] = re.sub('所在地区：', '', location.text)
    deposit = soup.find(lambda tag: tag.name=='div' and
                                    'charge' in tag.get('class', []) and
                                    re.compile('卖家当前保证金余额').search(tag.text))
    if deposit:
        chong['deposit'] = keep_float(deposit.find('span').text)

    seller_rate = soup.find('div', class_='box-chart')
    if seller_rate:
        chong['seller_rate'] = parse_seller_rate(seller_rate)

    dsr = soup.find('ul', id='dsr')
    if dsr:
        chong['dsr'] = {}
        chong['dsr']['match'] = parse_dsr(dsr, '宝贝与描述相符|服务质量')
        chong['dsr']['service'] = parse_dsr(dsr, '卖家的服务态度|服务态度')
        chong['dsr']['logistics'] = parse_dsr(dsr, '物流服务的质量|守时程度')
    return chong


def parse_seller_rate(seller_rate):
    chong = {}
    overall = seller_rate.find(lambda tag: tag.name == 'div' and
                                           'list' in tag.get('class', []) and
                                           re.compile('卖家信用').search(tag.text))
    chong['overall'] = keep_int(overall.text)
    main = seller_rate.find(lambda tag: tag.name=='div' and
                                        'list' in tag.get('class', []) and
                                        re.compile('主营行业').search(tag.text))
    chong['main'] = keep_int(main.text)
    return chong


def parse_dsr(dsr, pattern):
    chong = {}
    li = dsr.find(lambda tag: tag.name == 'li' and
                              'J_RateInfoTrigger' in tag.get('class', []) and
                              re.compile(pattern).search(tag.text))
    chong['score'] = keep_float(li.find('em').get('title'))
    compare_ind = li.find('strong', class_='percent')
    chong['compare_industry'] = 0 if 'normal' in compare_ind.get('class') else \
        keep_float(compare_ind.text) * (-1 if 'lower' in compare_ind.get('class') else 1)
    chong['total'] = keep_int(li.find('em', class_='h').find_next_sibling('span').text)
    for star in range(1, 6):
        star_div = li.find('div', class_='count{}'.format(star))
        chong['star{}'.format(star)] = keep_float(star_div.find('em', class_='h').text) \
            if star_div.find('em', class_='h') else 0.
    return chong


def parse_item(item, is_update=False):
    chong = {}
    timenow = datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S')
    chong['_id'] = item.get_attribute('data-id')
    listprice = item.find('span', class_='c-price')
    if listprice:
        chong['listprice'] = float(item.find('span', class_='c-price').text)
    cover_photo = item.find('dt', class_='photo')
    if cover_photo:
        chong['cover_photo'] = re.sub('_[0-9]+x[0-9]+\\.jpg$', '', cover_photo.find('img').get('src'))
    sold_30d = item.find('span', class_='sale-num')
    if sold_30d:
        if is_update:
            chong['sold_30d.{}'.format(timenow)] = int(sold_30d.text)
        else:
            chong['sold_30d'] = {timenow: int(sold_30d.text)}
    n_comments = item.find('dd', class_='rates')
    if n_comments:
        if is_update:
            chong['n_comments.{}'.format(timenow)] = int(n_comments.find('a').text)
        else:
            chong['n_comments'] = {timenow: int(n_comments.find('a').text)}
    return chong

def parse_itempage(fetcher,
                   attributes='title,stock,price,promo,comments,sales,bookmarks,cover,charity,attributes,description'):

    if not is_available(fetcher, '很抱歉，您查看的宝贝不存在，可能已下架或者被转移'):
        raise TaskDoneOther('TargetNoLongerAvailable')
    if fetcher.find('input', value='提交保证金', name='price') or fetcher.find('div', class_='J_AuctionContainer'):
        raise TaskDoneOther('TypeAuction')
    if re.compile('traveldetail\.taobao').search(fetcher.current_url):
        raise TaskDoneOther('TypeTravel')

    attributes = set(attributes.split(','))

    chong = dict()
    if 'title' in attributes:
        chong['title'] = fetcher.find('h3', class_='tb-main-title').text
    if 'stock' in attributes:
        chong['stock'] = 0 if fetcher.find('div', class_=re.compile('tb-off-sale')) else \
            keep_int(fetcher.find('span', id='J_SpanStock').text)
    if 'price' in attributes:
        chong['price'] = fetcher.find('strong', id='J_StrPrice').find_element_by_class_name('tb-rmb-num').text
    if 'promo' in attributes:
        promo = fetcher.find('em', id='J_PromoPriceNum')
        if promo:
            chong['promo'] = promo.text
    if 'comments' in attributes:
        chong['comments'] = keep_int(fetcher.find('strong', id='J_RateCounter').text)
        chong['n_comments.{}'.format(datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S'))] = chong['comments']
    if 'sales' in attributes:
        chong['sales'] = keep_int(fetcher.find('strong', id='J_SellCounter').text)
    if 'bookmarks' in attributes:
        chong['bookmarks'] = keep_int(fetcher.find('em', class_='J_FavCount').text)
    if 'cover' in attributes:
        cover = fetcher.find('ul', id='J_UlThumb')
        if cover:
            chong['cover'] = dict()
            video = cover.find_elements_by_id('J_VideoThumb')
            if video:
                fetcher.move_to(video[0])
                fetcher.find('button', class_=re.compile('vjs-center-start')).click()
                chong['cover']['video'] = fetcher.find('video', class_='lib-video').get_attribute('src')
            chong['cover']['images'] = [re.sub('_[0-9]+x[0-9]+\\.jpg$', '',
                                               img.find_element_by_tag_name('img').get_attribute('data-src'))
                                        for img in cover.find_elements_by_xpath('//li[@data-index]')
                                        if img.find_element_by_tag_name('img').get_attribute('data-src')]
    if 'charity' in attributes:
        charity = fetcher.find('div', id='J_PublicWelfare')
        if charity and charity.get_attribute('style') != 'display: none;':
            chong['charity'] = charity.find_element_by_class_name('infoBox').text
    if 'attributes' in attributes:
        chong['attributes'] = [re.split(u' *[:\uff1a] *', li.text)[-2:] for li in
                               fetcher.find('div', id='attributes').find_elements_by_tag_name('li')
                               if li.text.strip()]
    if 'description' in attributes:
        description = fetcher.find('div', id='J_DivItemDesc')
        if description:
            chong['description'] = {}
            if description.text:
                chong['description']['text'] = description.text.strip()
            chong['description']['images'] = [img.get_attribute('src')
                                              for img in description.find_elements_by_tag_name('img')]
    return chong


def parse_comments(fetcher):
    content = fetcher.find('body').text
    if not content:
        raise LookupError
    try:
        comments = json.loads(re.sub('\n|\r', '', content.strip()[27: -1]))
    except ValueError:
        comments = _json_loads(re.sub('\n|\r', '', content.strip()[27: -1]))
    total = comments.get('total', 0)
    comments = comments.get('comments')
    if not comments:
        raise TaskDoneOther('RateLimited')
    chongs = [comment for comment in comments]
    return total, chongs


def parse_comment_pages(fetcher):
    while True:
        if not fetcher.wait_until_not(lambda x: x.find_element_by_class_name('J_KgLoading_Message')) and \
                fetcher.session.find_element_by_class_name('J_KgLoading_Message').get_attribute('class') \
                == 'J_KgLoading_Message message failed':
            break

        if fetcher.find('a', class_='J_KgRate_Retry_Start'):
            fetcher.retry_with_click('click', fetcher.find('a', class_='J_KgRate_Retry_Start'),
                                     wait_until_not=lambda x: x.find_element_by_class_name('J_KgRate_Retry_Start'))

        _next = fetcher.wait_until(lambda x: x.find_element_by_class_name('pg-next'))
        time.sleep(1)
        if _next and _next.get_attribute('class') == 'pg-next':
            _next.click()
            if fetcher.find('a', class_='J_KgRate_Retry_Start'):
                fetcher.retry_with_click('click', fetcher.find('a', class_='J_KgRate_Retry_Start'),
                                         wait_until_not=lambda x: x.find_element_by_class_name('J_KgRate_Retry_Start'))
        elif fetcher.find('a', class_='J_KgRate_ToggleFoldedReviews'):
            fetcher.find('a', class_='J_KgRate_ToggleFoldedReviews').click()
            fetcher.wait_until(lambda x: x.find_element_by_class_name('J_KgRate_FoldedBd'))
            if fetcher.find('a', class_='J_KgRate_Retry_Start'):
                fetcher.retry_with_click('click', fetcher.find('a', class_='J_KgRate_Retry_Start'),
                                         wait_until_not=lambda x: x.find_element_by_class_name('J_KgRate_Retry_Start'))
            break
        else:
            break

    urls = [item['request']['url'] for item in fetcher.proxy.har['log']['entries']
            if re.compile('feedRateList').search(item["request"]['url'])]
    return [url for url in urls if 'folded=0' in url], [url for url in urls if 'folded=1' in url]


def parse_shopid_from_itempage(fetcher):
    if not is_available(fetcher, '很抱歉，您查看的宝贝不存在，可能已下架或者被转移'):
        return None

    page_property = fetcher.find('script', text=re.compile('var g_config'))
    if page_property:
        shopid_line = [line.strip('\t },;') for line in re.split('\n', page_property.get_text())
                       if line.strip('\t },;').startswith('shopId')]
        if shopid_line:
            return re.compile(': +\'([0-9]+)\'').search(shopid_line[0]).group(1)
    return None


def is_available(fetcher, text):
    if fetcher.find('div', class_='error-notice-hd', text=re.compile(text)):
        return False
    return True


def _json_loads(text):
    count = 0
    while True:
        try:
            return json.loads(text)
        except ValueError as e:
            count += 1
            if "Expecting ',' delimiter" not in e.args[0] or count > 100:
                raise e
            # text = re.sub('(\"content\":\"[^"]+)\"([^"]+\"[}]]*,\")', '\g<1>\g<2>', text)
            # text = re.sub('(\"content\":\"[^"]+)\"([^"]+)\"([^"]+\"[}]]*,\")', '\g<1>\g<2>\g<3>', text)
            text = re.sub('(\"content\":\"[^"]*)\"([^,}\]])', '\g<1>\g<2>', text)

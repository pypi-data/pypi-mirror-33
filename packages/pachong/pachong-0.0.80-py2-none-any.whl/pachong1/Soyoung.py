#-*-coding:utf-8-*-
__author__ = 'cchen'


from pachong import PaChong
import re


class Soyoung(PaChong):

    def crawl_product(self, pids, fp_products, fp_diary_groups, fp_diaries, fp_comments):
        products = [[pid] + self._crawl_product(pid, fp_diary_groups, fp_diaries, fp_comments)
                    for pid in pids]
        self.write_records(products, fp_products)

    def _crawl_product(self, pid, fp_diary_groups, fp_diaries, fp_comments):
        print pid
        # basic info
        soup = self.get_soup('http://y.soyoung.com/cp{}'.format(pid))
        basic_info = soup.find('div', class_='basic-info')
        title = basic_info.h1.get_text(strip=True).encode('utf-8')
        base_price = basic_info.find('div', class_='base-price')
        # [rmb.extract() for rmb in price.find_all('i')]
        promo = base_price.find('em')
        promo.i.extract()
        promo = promo.get_text(strip=True)
        msrp = base_price.find('del')
        msrp.i.extract()
        msrp = msrp.get_text(strip=True)
        base_relation = basic_info.find('div', class_='base-relation')
        reservations = base_relation.find_all('div', class_=re.compile('sub'))[-1].em.text
        images = '|'.join(self.get_image_url(img.get('data-src'))
                          for img in soup.find_all('li', class_='js-slide-min'))

        # diary info
        data = self.get_json('http://y.soyoung.com/cp{}?action=calendarlist'.format(pid))
        tags = '|'.join(tag['tag_name'] + ':' + tag['cnt']
                        for tag in data['product']['tag']).encode('utf-8')
        rvws = dict((rvw['record_notice'].strip(), float(rvw['record_value']))
                    for rvw in data['product']['record']['record'])
        overall = rvws.get(u'\u6ee1\u610f\u5ea6', '')
        enviroment = rvws.get(u'\u73af\u5883', '')
        profession = rvws.get(u'\u4e13\u4e1a\u5ea6', '')
        servicenss = rvws.get(u'\u670d\u52a1', '')
        effectness = rvws.get(u'\u6548\u679c', '')

        n_diaries = int(data['group_list']['cnt'])
        diary_group_ids = [diary['group_id'] for diary in data['group_list']['list']]
        diary_groups = [[pid] + self._crawl_diary_group(diary_group_id, fp_diaries, fp_comments)
                        for diary_group_id in diary_group_ids]
        self.write_records(diary_groups, fp_diary_groups)

        return [title, msrp, promo,
                images, reservations, tags,
                overall, enviroment, profession, servicenss, effectness,
                n_diaries, '|'.join(diary_group_ids)]

    def _crawl_diary_group(self, gid, fp_diaries, fp_comments):
        print '\t' + gid
        soup = self.get_soup('http://www.soyoung.com/dpg{}'.format(gid))
        diary_info = soup.find('div', class_='diary-info')
        user = diary_info.find('div', class_='avatar-box')
        user_img = user.img.get('src')
        user_name = user.img.get('alt').encode('utf-8')
        user_id = self.get_id(user.a.get('href'))
        user_gender = user.find('span', class_='dp-icon').get('class')[-1][0]
        info = {}
        for row in diary_info.find('div', class_='info-box').find_all('div', class_='row'):
            if row.find('div', class_='field'):
                field = row.find('div', class_='field')
                value = row.find('div', class_='value')
                info[field.get_text(strip=True)] = value.get_text(strip=True)
                if value.find('a') and value.find('a').get_text(strip=True):
                    info[field.get_text(strip=True)] += '@' + self.get_id(value.a.get('href'))
            elif row.find('div', class_='img-field'):
                value = row.find('div', class_='before-photos')
                info[u'before_photos'] = '|'.join(url.get('href') for url in value.find_all('a'))
        surgery_cate = info.get(u'\u9879\u76ee\uff1a', '').encode('utf-8')
        surgery_time = info.get(u'\u65e5\u671f\uff1a', '').encode('utf-8')
        surgery_name = info.get(u'\u4ea7\u54c1\uff1a', '').encode('utf-8')
        surgery_where = info.get(u'\u533b\u9662\uff1a', '').encode('utf-8')
        surgery_doctr = info.get(u'\u533b\u751f\uff1a', '').encode('utf-8')
        surgery_price = info.get(u'\u4ef7\u683c\uff1a', '').encode('utf-8')
        surgery_before = info.get(u'before_photos', '')

        diary_ids = [self.get_id(diary.find('div', class_='other-box').a.get('href'))
                     for diary in soup.find_all('li', class_='diary-item')]

        diaries = [[gid] + self._crawl_diary(diary_id, gid, fp_comments)
                   for diary_id in diary_ids]
        self.write_records(diaries, fp_diaries)

        return [gid,
                user_id, user_name, user_img, user_gender,
                len(diary_ids),
                surgery_cate, surgery_time, surgery_where, surgery_doctr,
                surgery_name, surgery_price, surgery_before]

    def _crawl_diary(self, did, gid, fp_comments):
        print '\t\t' + did
        soup = self.get_soup('http://www.soyoung.com/p{}?group_id='.format(did, gid))
        [font_icon.extract() for font_icon in soup.find_all('span', class_='font_icon')]
        days = int(soup.find('span', class_='day').text)
        symptoms = {}
        for symptom in soup.find('ul', class_='level_list').find_all('li'):
            if symptom.find('span', class_='sym'):
                field = symptom.find('span', class_='t').get_text(strip=True)
                value = symptom.find('span', class_='sym').get_text(strip=True)
                symptoms[field] = value
            elif symptom.find('span', class_='level'):
                field = symptom.find('span', class_='t').get_text(strip=True)
                value = float(re.compile('width: (.*);$')
                              .search(symptom.find('span', class_='level').span.get('style'))
                              .group(1)[:-1]) / 100
                symptoms[field] = value
        symptom = symptoms.get(u'\u75c7\u72b6\uff1a', '').encode('utf-8')
        satisfaction = symptoms.get(u'\u6ee1\u610f\u5ea6\uff1a', '')
        swelling = symptoms.get(u'\u80bf\u80c0\u5ea6\uff1a', '')
        pain = symptoms.get(u'\u75bc\u75db\u611f\uff1a', '')
        scar = symptoms.get(u'\u75a4\u75d5\u5ea6\uff1a', '')

        content = soup.find('div', class_='c')
        [emo.insert(0, self.get_emoticon(emo.get('src')))
         for emo in content.find_all('img', class_='img_motion')]
        text = content.get_text(' ', strip=True).encode('utf-8')
        imgs = '|'.join(self.get_image_url(media.find(lambda tag: tag.has_attr('src')).get('src'))
                        for media in content.find_all('p', class_=re.compile('image|video')))

        status = soup.find('div', class_='status')
        n_views = status.find('a').get_text(strip=True)
        n_likes = status.find('a', id=re.compile('up_cnt')).get_text(strip=True)
        n_comms = status.find('a', class_='reply_btn').get_text(strip=True)
        created = status.find('span', class_='time').get_text(strip=True)
        comments = [[did] + self.parse_reply(reply)
                    for reply in soup.find_all('li', id=re.compile('reply-'))]

        if soup.find('div', class_='pages'):
            pages = set()
            for page in soup.find('div', class_='pages').find_all('a'):
                try:
                    pages.add(int(page.get_text(strip=True)))
                except ValueError:
                    pass
            for i_page in range(2, sorted(pages)[-1] + 1):
                soup = self.get_soup('http://www.soyoung.com/p{}?page={}'.format(did, i_page))
                comments += [[did] + self.parse_reply(reply)
                        for reply in soup.find_all('li', id=re.compile('reply-'))]
        self.write_records(comments, fp_comments)

        return [did,
                days, text, imgs, created,
                symptom, satisfaction, swelling, pain, scar,
                n_views, n_likes, n_comms]

    def parse_reply(self, reply):
        rid = re.sub('^reply-', '', reply.get('id'))
        print '\t\t\t' + rid
        usr = reply.find('a', class_='name')
        uid = ('y' if 'hp' in usr.get('class') else '') + self.get_id(usr.get('href'), '0')
        [emo.insert(0, self.get_emoticon(emo.get('src')))
         for emo in reply.find_all('img', class_='img_motion')]
        content = reply.find('div', class_='reply_c').get_text(' ', strip=True).encode('utf-8')
        status = reply.find('div', class_='status')
        n_likes = status.find('a', id=re.compile('reply_ding_cnt')).get_text(strip=True)
        created = status.find('span', class_='time').get_text(strip=True)
        n_replies = status.find('a', id=re.compile('reply_comment_cnt')).get_text(strip=True)
        return [rid,
                uid, content, created, n_likes, n_replies]

    @staticmethod
    def get_emoticon(url):
        return ':' + re.compile('([0-9]+)\.(png|gif)$').search(url).group(1) + ':'

    @staticmethod
    def get_image_url(url):
        return re.sub('_[0-9]+\.jpg$', '.jpg', url)

    @staticmethod
    def get_id(url, default=''):
        try:
            return re.compile('/[a-zA-Z]*([0-9]+)$').search(url).group(1)
        except AttributeError:
            return default

# self = Soyoung()
# self.crawl_product(['12385'],
#                    'sy_products.tsv',
#                    'sy_diarygroup.tsv',
#                    'sy_diaries.tsv',
#                    'sy_diarycomments.tsv')
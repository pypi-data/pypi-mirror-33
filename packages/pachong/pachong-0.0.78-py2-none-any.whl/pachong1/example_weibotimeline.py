#-*-coding:utf-8-*-
__author__ = 'cchen'


from weibo import Weibo
import time


while True:
    crawler = Weibo()
    while True:
        try:
            crawler.login('0012028475117', 'Cc19900201')
            break
        except:
            print 'retry login'
            time.sleep(60)
    crawler.crawl_timeline('../../pachong2/weibozhuliren_timeline.tsv',
                           '../../pachong2/weibozhuliren_profile.tsv',
                           30)
    time.sleep(3*60)
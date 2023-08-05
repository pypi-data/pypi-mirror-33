#-*-coding:utf-8-*-
__author__ = 'cchen'


from pachong import PaChong


self = PaChong()

class Taobao(PaChong):

    def crawl_merchandise(self):
        soup = self.get_soup('https://item.taobao.com/item.htm?spm=a1z10.4-c-s.w5003-17306208047.2.6f071edaLyt6AB&id=560795384872&scene=taobao_shop')



from selenium import webdriver
driver = webdriver.PhantomJS('/Users/cchen/Programs/phantomjs-2.1.1/bin/phantomjs')
html = driver.get('https://item.taobao.com/item.htm?spm=a1z10.4-c-s.w5003-17306208047.2.6f071edaLyt6AB&id=560795384872&scene=taobao_shop')

driver.get('https://weibo.com/u/5581331908?profile_ftype=1&is_all=1#_0')
driver.save_screenshot('screen.png')


header = {'_host': 'detailskip011133075207.unzbyun.na61',
'content-encoding': 'gzip',
'content-type': 'text/plain;charset=GBK',
'eagleeye-traceid': '42c618d515102698410494156e',
'eagleid': '42c618d515102698410494156e',
'date':'Thu, 09 Nov 2017 23:24:01 GMT',
'p3p': 'CP=CURa ADMa DEVa PSAo PSDo OUR BUS UNI PUR INT DEM STA PRE COM NAV OTC NOI DSP COR',
's': 'STATUS_NORMAL',
'server': 'Tengine',
'set-cookie': '_tb_token_=7ee5087b44b63; Domain=.taobao.com; Path=/',
'status': '200',
'strict-transport-security': 'max-age=31536000',
'timing-allow-origin': '*, *',
'trace_id': '42c618d515102698410494156e',
'ufe-result': 'A6',
'via': 'bcache3.us4[716,0]',}

self.session.get('https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId=560795384872&sellerId=105452356&modules=dynStock,qrcode,viewer,price,duty,xmpPromotion,delivery,activity,fqg,zjys,couponActivity,soldQuantity,originalPrice,tradeContract&callback=onSibRequestSuccess', headers=header)
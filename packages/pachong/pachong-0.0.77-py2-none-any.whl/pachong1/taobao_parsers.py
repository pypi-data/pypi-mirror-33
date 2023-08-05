#-*-coding:utf-8-*-
__author__ = 'cchen'



def parse_merchandise(soup):
    # title, subtitle, is_ifashion, seller
    # orginal price, promo price,
    # details, pics

    with open('test.html', 'w') as o:
        o.write(soup.prettify().encode('utf-8'))



    title = soup.find('h3', class_='tb-main-title').get_text(strip=True)
    subtitle = soup.find('p', class_='tb-subtitle').get_text(strip=True)


    start_price = soup.find('strong', id='J_StrPrice').find('em', class_='tb-rmb-num').get_text(strip=True)
    promo_price = soup.find('strong', class_='tb-promo-price').find('em', class_='tb-rmb-num').get_text(strip=True)
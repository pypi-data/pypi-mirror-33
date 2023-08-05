#-*-coding:utf-8-*-
__author__ = 'cchen'


from pachong import PaChong
import urllib
import json


class instagram(PaChong):

    def login(self, username, password):
        username='cchenapp'
        password='Cc19900201'
        login_page = self.session.get('https://www.instagram.com/accounts/login/')
        self.session.post('https://www.instagram.com/accounts/login/ajax/',
                          data={'username': 'cchenapp', 'password': 'Cc19900201'})

    def crawl_likers(self, media_id):
        query = {
            'query_id': '17890626976041463',
            'variables': '{"shortcode":"BEYjooAw8A8","first":20}',
        }
        # urllib.urlencode(query)

        data = self.get_json('https://www.instagram.com/graphql/query/', params=query)

self = PaChong()

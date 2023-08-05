#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/27/18
# @File  : [pachong] selenium.py


from __future__ import absolute_import
from __future__ import unicode_literals

import random
import re
import time
from os import path

from browsermobproxy import Server
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from six import iteritems
from six.moves.urllib.parse import urlencode

from .base import Fetcher


class Browser(Fetcher):
    MAX_RETRIES = 9
    MAX_WAITTIME = 60 * 5
    STATUS_FORCELIST = [500]

    def __init__(self, session=None, proxy=None, load_images=True, use_network=False):
        self.proxy = proxy
        self.use_network = use_network
        self.load_images = load_images
        self.session = session

    def get(self, url, **kwargs):
        params = kwargs.get('params')
        sleep = kwargs.get('sleep', 5 + random.random() * 5)
        if params:
            delimiter = kwargs.get('delimiter', '?')
            url += delimiter + urlencode(params)
        until = kwargs.get('until')
        until_not = kwargs.get('until_not')

        for x in range(self.MAX_RETRIES + 1):
            try:
                self.session.get(url)
                self.soup = self.build_soup()
                time.sleep(sleep)
                if until:
                    uu = self.wait_until(until)
                    return uu if uu else self.get(url, **kwargs)
                if until_not:
                    un = self.wait_until_not(until_not)
                    return un if un else self.get(url, **kwargs)
                return True
            except (TimeoutException, WebDriverException):
                continue
        raise TimeoutException

    def build_soup(self):
        return BeautifulSoup(self.session.page_source, 'lxml')

    def find(self, *args, **kwargs):
        try:
            if 'xpath' in kwargs:
                return self.session.find_element_by_xpath(kwargs['xpath'])
            if len(args) == 2:
                kwargs = args[1]
            if 'class_' in kwargs:
                kwargs['class'] = kwargs['class_']
                kwargs.pop('class_')
            xpath = '//' + args[0]
            if kwargs:
                xpath += '[' + \
                         ' and '.join(
                             'contains({}, "{}")'.format('text()' if k == 'text' else '@' + k, v.pattern)
                             if isinstance(v, re._pattern_type) else
                             '@{}="{}"'.format(k, v)
                             for k, v in iteritems(kwargs)
                         ) + \
                         ']'
            return self.session.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return None

    def find_all(self, *args, **kwargs):
        if 'xpath' in kwargs:
            return self.session.find_elements_by_xpath(kwargs['xpath'])
        if len(args) == 2:
            kwargs = args[1]
        if 'class_' in kwargs:
            kwargs['class'] = kwargs['class_']
            kwargs.pop('class_')
        xpath = '//' + args[0] + '[' + ' and '.join('@{}="{}"'.format(k, v) for k, v in iteritems(kwargs)) + ']'
        return self.session.find_elements_by_xpath(xpath)

    def source_code(self):
        return self.session.page_source

    def save(self, fp_out):
        with open(fp_out, 'w') as o:
            o.write(self.source_code())

    def wait_until(self, until, waittime=30):
        if until and not callable(until):
            raise TypeError('until must be a function.')
        try:
            response = WebDriverWait(self.session, waittime).until(until)
        except TimeoutException:
            response = None
        self.soup = self.build_soup()
        return response

    def wait_until_not(self, until_not, waittime=30):
        if until_not and not callable(until_not):
            raise TypeError('until_not must be a function.')
        try:
            response = WebDriverWait(self.session, waittime).until_not(until_not)
        except TimeoutException:
            response = None
        self.soup = self.build_soup()
        return response

    def move_to(self, ele):
        actions = ActionChains(self.session)
        actions.move_to_element(ele)
        actions.perform()
        time.sleep(1)

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, val):
        if val == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--incognito")
            if self.proxy:
                chrome_options.add_argument('--proxy-server=%s' % self.proxy)
            if not self.load_images:
                pass #TODO
            self._session = webdriver.Chrome('/Users/cchen/Programs/webdriver/chromedriver', chrome_options=chrome_options)
        elif val == 'firefox':
            firefox_profile = webdriver.FirefoxProfile()
            firefox_profile.set_preference("browser.privatebrowsing.autostart", True)
            if self.use_network:
                PROXY_PATH = path.abspath('./browsermob/bin/browsermob-proxy.bat')
                # PROXY_PATH = "/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/browsermob/bin/browsermob-proxy.bat"
                server = Server(PROXY_PATH)
                server.start()
                self.proxy = server.create_proxy()
                firefox_profile.set_proxy(self.proxy.selenium_proxy())
            if not self.load_images:
                firefox_profile.set_preference('permissions.default.image', 2)
            self._session = webdriver.Firefox(firefox_profile=firefox_profile)
            self._session.set_page_load_timeout(self.MAX_WAITTIME)
        else:
            self._session = val

    def retry_with_click(self, element, wait_until=None, wait_until_not=None):
        for x in range(self.MAX_RETRIES + 1):
            element.click()
            if wait_until:
                w = self.wait_until(wait_until)
                if w:
                    return w
            elif wait_until_not:
                w = self.wait_until_not(wait_until_not)
                if w:
                    return w
            else:
                raise AttributeError('Either wait_until or wait_until_not must have value.')
        raise NotImplementedError('Reached max retries.')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/24/18
# @File  : [pachong] webdrivers.py

from __future__ import absolute_import
from __future__ import unicode_literals

import re

from future.builtins import range
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.webdriver import WebDriver as _FirefoxWebDriver
from selenium.webdriver.firefox.webelement import FirefoxWebElement as _FirefoxWebElement
from selenium.webdriver.remote.command import Command
from selenium.webdriver.remote.webdriver import WebDriver as _RemoteWebDriver
from selenium.webdriver.remote.webelement import WebElement as _RemoteWebElement
from selenium.webdriver.support.wait import WebDriverWait
from six import iteritems
from six.moves.urllib.parse import urlencode


class RemoteWebElement(_RemoteWebElement):

    def find(self, tag_name=None, attrs=None, **kwargs):
        try:
            xpath = self._wrap_xpath(tag_name, attrs, **kwargs)
            return self.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return None

    def find_all(self, tag_name=None, attrs=None, **kwargs):
        xpath = self._wrap_xpath(tag_name, attrs, **kwargs)
        return self.find_elements_by_xpath(xpath)

    def get(self, name):
        return self.get_attribute(name)

    def get_text(self, *args, **kwargs):
        return self.get_attribute('text')

    @staticmethod
    def _wrap_xpath(tag_name=None, attrs=None, **kwargs):
        # TODO text() for all children. (also soup)

        if 'xpath' in kwargs:
            return kwargs['xpath']

        if 'class_' in kwargs:
            kwargs['class'] = kwargs.pop('class_')
        xpath = './/'
        if tag_name:
            xpath += tag_name
        if attrs is not None:
            kwargs.update(attrs)
        if kwargs:
            xpath += '[' + \
                     ' and '.join(
                         'contains({}, "{}")'.format('text()' if k == 'text' else '@' + k, v.pattern)
                         if isinstance(v, re._pattern_type) else
                         '@{}="{}"'.format(k, v)
                         for k, v in iteritems(kwargs)
                     ) + \
                     ']'
        return xpath


class RemoteWebDriver(_RemoteWebDriver, RemoteWebElement):
    _web_element_cls = RemoteWebElement
    MAX_RETRIES = 9

    def get(self, url, **kwargs):
        params = kwargs.get('params')
        if params:
            delimiter = kwargs.get('delimiter', '?')
            url += delimiter + urlencode(params)
        for _ in range(self.MAX_RETRIES + 1):
            try:
                return self._get(url)
            except (TimeoutException, WebDriverException):
                continue
        raise TimeoutException

    def _get(self, url):
        self.execute(Command.GET, {'url': url})
        return self

    def until(self, method, timeout=30, timeout_increment=5):
        if not callable(method):
            raise TypeError('method must be a function.')
        response = None
        for _ in range(self.MAX_RETRIES + 1):
            try:
                return WebDriverWait(self, timeout).until(method)
            except TimeoutException:
                timeout += timeout_increment
        return response

    def until_not(self, method, timeout=30, timeout_increment=5):
        if not callable(method):
            raise TypeError('method must be a function.')
        response = None
        for _ in range(self.MAX_RETRIES + 1):
            try:
                return WebDriverWait(self, timeout).until_not(method)
            except TimeoutException:
                timeout += timeout_increment
        return response

    @property
    def action_chains(self):
        return ActionChains(self)


class FirefoxWebElement(_FirefoxWebElement, RemoteWebElement):
    pass


class Firefox(_FirefoxWebDriver, RemoteWebDriver):
    _web_element_cls = FirefoxWebElement

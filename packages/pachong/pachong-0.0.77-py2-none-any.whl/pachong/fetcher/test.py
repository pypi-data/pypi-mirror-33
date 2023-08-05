#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/23/18
# @File  : [pachong] test.py



from bs4 import BeautifulSoup as bs4BeautifulSoup
from bs4.element import Tag as bs4Tag


class BeautifulSoup(bs4BeautifulSoup):
    pass


class Tag(bs4Tag):
    pass

with open('/Users/cchen/Desktop/huodong.html', 'r') as i:
    soucepage = i.read()
soup = BeautifulSoup(soucepage, 'lxml')
div = soup.find('div')
i = div.find('i')
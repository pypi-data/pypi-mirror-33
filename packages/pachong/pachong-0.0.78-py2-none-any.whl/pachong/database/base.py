#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 2/13/18
# @File  : [pachong] base.py


import warnings
import json


class Database(object):

    def insert(self, document):
        raise NotImplementedError

    def insert_many(self, documents):
        raise NotImplementedError

    def find(self, match, fields=None):
        raise NotImplementedError

    def find_all(self, match, fields=None):
        raise NotImplementedError

    def drop(self, match):
        raise NotImplementedError

    def update(self, match, document, method='$set'):
        raise NotImplementedError

    def import_data(self, data, is_json=False):
        if not isinstance(data, (list, set)):
            with open(data, 'r') as i:
                data = [line.strip() for line in i if line.strip()]
        if is_json:
            [self.insert(json.loads(target)) for target in data]
        else:
            [self.insert(target) for target in data]
        return self

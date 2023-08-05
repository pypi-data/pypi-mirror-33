#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 4/7/18
# @File  : [pachong] pachong.py


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import inspect
import json
import traceback
from datetime import datetime
from os import path

from tqdm import tqdm

from ..setting_logger import Logger
from .common.exceptions import TaskDoneOther
from datetime import datetime, timedelta
import time
import random


class Pachong(object):

    tasks_available = []

    def __init__(self, project, input_, output='', fetcher=None, Database=None, batch=0, machine=0):
        self.batch = batch
        self.machine = machine
        self.project = project
        self.Database = Database
        self.input_ = input_
        self.output = output
        self.fetcher = fetcher
        self.logger = Logger(project + '_' + (input_ if self.input_ is self.output else output) + '.log')
        self.input_list = []
        self.samples = []
        self.max_time = None
        self.enforce_update = False

    def crawl(self, task, sleep=random.random() * 5 + 3, is_update=True):
        t0 = datetime.now()
        self.task = task
        print('Starting task: {}'.format(task))
        self.samples = self.sample_input(self.batch, self.batch * self.machine)
        with tqdm(self.samples) as bar:
            for target in bar:
                target_id = target['_id']
                bar.set_description(target_id)
                timenow = datetime.utcnow()
                try:
                    if self.input_ is self.output or self.enforce_update or is_update:
                        [self.output.update(target_id, chong)
                         for chong in eval('self.{}(target)'.format(self.task))
                         if chong]
                    else:
                        [self.output.insert(chong)
                         for chong in eval('self.{}(target)'.format(self.task))
                         if chong]
                    self.logger.push('DATABASE', '{} is done.'.format(target_id))
                    self.input_.update(target_id, {'task.{}.status'.format(self.task): 'done',
                                                   'task.{}.datetime'.format(self.task): timenow})
                    self.input_.drop_field(target_id, 'task.{}.traceback'.format(self.task))
                except TaskDoneOther as taskdone_error:
                    self.input_.update(target_id, {'task.{}.status'.format(self.task): 'done',
                                                   'task.{}.other'.format(self.task): taskdone_error.other,
                                                   'task.{}.datetime'.format(self.task): timenow})
                except Exception:
                    self.traceback = traceback.format_exc()
                    self.input_.update(target_id, {'task.{}.status'.format(self.task): 'error',
                                                   'task.{}.traceback'.format(self.task): self.traceback,
                                                   'task.{}.datetime'.format(self.task): timenow})
                t1 = datetime.now()
                if self.max_time is not None and (t1 - t0).seconds > self.max_time:
                    break

                time.sleep(sleep)
        return self

    def import_input(self, filepath=None, input_list=None, update=False, is_json=False):
        if not update and self.input_.collection.name in set(self.output.db.collection_names()):
            self.logger.push('DATABASE', 'Input already exists.')
            return self

        else:
            if filepath and input_list is None:
                with open(filepath, 'r') as i:
                    input_list = [line.strip() for line in i if line.strip()]
            import_count = sum([self.input_.insert(json.loads(target))
                                if is_json else self.input_.insert(target)
                                for target in input_list])
            self.logger.push('DATABASE', 'Imported {} inputs to crawl.'.format(import_count))

            if input_list:
                self.input_list = input_list

        return self

    def captcha_handler(self):
        raise LookupError

    def sample_input(self, n_sample=None, skip=None):
        cursor = self.input_.find_all({
            '_id': {'$in': self.input_list} if self.input_list else {'$exists': True},#})
            '$or': [{'task.{}.datetime'.format(self.task): {'$exists': False}},
                    {'task.{}.datetime'.format(self.task): {'$lt': datetime.utcnow() - timedelta(days=14)}},
                    {'task.{}.status'.format(self.task): {'$ne': 'done'}}],
        })
        # 'task.{}.status'.format(self.task): {'$nin': ['done']},})
        # cursor = self.input_.find_all({'task.{}.status'.format(self.task): {'$nin': ['done']},
        #                                'task.comments.status': {'$in': ['done', 'error']}})
        # with open('/Users/cchen/GoogleDrive/porkspace/packages/pachong/pachong/itemids15.txt', 'r') as i:
        #     sample = [line.strip() for line in i if line.strip()]
        # cursor = self.input_.find_all({'_id': {'$in': sample},
        #                                'task.{}.status'.format(self.task): {'$nin': ['done']}})
        return list(cursor.skip(skip).limit(n_sample)) if n_sample else list(cursor.skip(skip))

    @staticmethod
    def utc_now():
        return (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()

    @property
    def input_(self):
        return self._input_

    @input_.setter
    def input_(self, val):
        if val == '':
            raise AttributeError('Input name is required')
        self._input_ = self.Database(self.project, val)

    # @property
    # def profile(self):
    #     return self._profile
    #
    # @profile.setter
    # def profile(self, val):
    #     if val == '':
    #         raise AttributeError('Input name is required')
    #     self._profile = self.Database(self.project, val)

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, val):
        self._output = self.input_ if not val else self.Database(self.project, val)
        self.logger = Logger(self.project + '_' +
                             (self.input_.collection.name if self.input_ is self.output
                              else self.output.collection.name) + '.log')
    @property
    def fetcher(self):
        return self._fetcher

    @fetcher.setter
    def fetcher(self, val):
        if val is None:
            raise AttributeError('Fetcher is NoneType')
        self._fetcher = val

    @property
    def Database(self):
        return self._Database

    @Database.setter
    def Database(self, val):
        if val is None:
            raise AttributeError('Database is NoneType')
        self._Database = val

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, val):
        if val not in self.tasks_available:
            raise LookupError('Available task options are {}'.format(self.tasks_available))
        if not isinstance(self.fetcher, self.tasks_available[val]):
            raise TypeError('Fetcher type wrong.')
        self._task = val

    @property
    def __dir__(self):
        return path.dirname(path.abspath(inspect.getfile(inspect.currentframe())))

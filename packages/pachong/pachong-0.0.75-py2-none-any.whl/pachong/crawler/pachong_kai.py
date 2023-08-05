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
import traceback
from datetime import datetime
from itertools import chain
from os import path

from tqdm import tqdm

from .common.exceptions import TaskDoneOther
from ..setting_logger import Logger


class Pachong(object):
    tasks_available = []

    def __init__(self, input_=None, output=None, fetcher=None, task=None):
        self.input_ = input_
        self.output = output
        self.fetcher = fetcher

    def crawl(self, task, targets=None):
        self.task = task
        print('Starting task: {}'.format(self.task))
        if targets is None:
            cursor = self.input_.find_all({'_id': {'$in': self.input_list} if self.input_list else {'$exists': True},
                                           'task.{}.status'.format(self.task): {'$nin': ['done']},})
        with tqdm(targets) as bar:
            for target in bar:
                if not isinstance(target, dict):
                    target = {'_id': target}
                target_id = target['_id']
                bar.set_description(target_id)
                try:

                    if self.input_ is self.output or self.enforce_update:
                        [self.output.update(target_id, chong)
                         for chong in eval('self.{}(target)'.format(self.task))
                         if chong]
                    else:
                        [self.output.insert(chong)
                         for chong in eval('self.{}(target)'.format(self.task))
                         if chong]
                    self.logger.push('DATABASE', '{} is done.'.format(target_id))
                    self.input_.update(target_id, {'task.{}.status'.format(self.task): 'done'})
                    self.input_.drop_field(target_id, 'task.{}.traceback'.format(self.task))
                except TaskDoneOther as taskdone_error:
                    self.input_.update(target_id, {'task.{}.status'.format(self.task): 'done',
                                                   'task.{}.other'.format(self.task): taskdone_error.other})
                except Exception:
                    self.traceback = traceback.format_exc()
                    self.input_.update(target_id, {'task.{}.status'.format(self.task): 'error',
                                                   'task.{}.traceback'.format(self.task): self.traceback})
                t1 = datetime.now()
                if self.max_time is not None and (t1 - t0).seconds > self.max_time:
                    break
        return self

    def captcha_handler(self):
        raise LookupError

    @staticmethod
    def utc_now():
        return (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()

    @property
    def targets(self):
        return self._targets

    @targets.setter
    def targets(self, val):
        if val is None:
            self._targets = list(self.input_.find_all({'task.{}.status'.format(self.task): {'$nin': ['done']}, }))
        else:
            if not isinstance(val[0], dict):
                val = [{'_id': v} for v in val]
            batchsize = 100000
            if len(val) < batchsize:
                cursor = self.input_.find_all({'_id': {'$in': [v['_id'] for v in val]},
                                               'task.{}.status'.format(self.task): {'$in': ['done']},})
                done = {doc['_id'] for doc in cursor}
            else:
                done = set()
                for x in range(len(val) // batchsize + (len(val) % batchsize > 0)):
                    cursor = self.input_.find_all(
                        {'_id': {'$in': [v['_id'] for v in val[batchsize * x: batchsize * (x + 1)]]},
                         'task.{}.status'.format(self.task): {'$in': ['done']}, })
                    done |= {doc['_id'] for doc in cursor}
            self._targets = [target for target in val if target['_id'] not in done]

    @property
    def fetcher(self):
        return self._fetcher

    @fetcher.setter
    def fetcher(self, val):
        if val is None:
            raise AttributeError('Fetcher is NoneType')
        self._fetcher = val

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


        t0 = datetime.now()


    def captcha_handler(self):
        raise LookupError


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
    def Database(self):
        return self._Database

    @Database.setter
    def Database(self, val):
        if val is None:
            raise AttributeError('Database is NoneType')
        self._Database = val




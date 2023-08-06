#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.worker.base
    ~~~~~~~~~~~~

    This module provide the base worker.

    :copyright: (c) 2017 by Ma Fei.
"""
import json
import logging
import os
import time

from agent.api.qualityplatform import QualityPlatform
from agent.consts import TaskStatus
from agent.util.tools import FTPToolKit

logger = logging.getLogger(__name__)

qualityplatform_client = QualityPlatform()

ftp_client = FTPToolKit()


class BaseWorker(object):
    def __init__(self, data):
        task = qualityplatform_client.get_task_by_id(data)
        worker_data = json.loads(task.get('params'))
        self.task_id = data
        self.task_type = task.get('task_type')
        self.retry_count = task.get('retry_count')
        self.data = worker_data

    def start_worker(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def complete(self):
        qualityplatform_client.update_task_status(self.task_id, TaskStatus.success.value)

    @staticmethod
    def upload(localdir, remotedir):
        ftp_client.upload(localdir, remotedir)

    def run(self):
        try:
            qualityplatform_client.update_task_status(self.task_id, TaskStatus.running.value)
            self.start_worker()
        except Exception as e:
            self.clear()
            logger.error('got worker exception in run worker task {}: {}'.format(
                self.task_id, repr(e.message), exe_info=True))
            qualityplatform_client.update_task_status(self.task_id, TaskStatus.failed.value)
            self.retry()

    def retry(self):
        count = 0
        log = ''
        while count < self.retry_count:
            try:
                time.sleep(1)
                self.start_worker()
            except Exception as e:
                self.clear()
                log += 'retry {} time failed: {} | '.format(count, repr(e))
                logger.error('got exception in retry worker task {} loop {}: {}'.format(
                    self.task_id, count, e.message), exe_info=True)
                qualityplatform_client.update_task_status(self.task_id, TaskStatus.failed.value)
            count += 1
            if count == self.retry_count:
                logger.error(
                    'retry worker task {} failed {} times : {}'.format(
                        self.task_id, count, log), exe_info=True)
                raise

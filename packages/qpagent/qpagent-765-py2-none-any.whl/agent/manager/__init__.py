#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.queue
    ~~~~~~~~~~~

    This module provide the worker queue.

    :copyright: (c) 2018  by Ma Fei.
"""
import Queue
import logging
from threading import Lock
from threading import Thread

from agent.consts import AgentWorkerType
from agent.worker.monkey import AndroidMonkey

logger = logging.getLogger(__name__)
android_monkey_mutex = Lock()


class TaskQueue(Queue.Queue):
    def __init__(self, num_workers=1):
        Queue.Queue.__init__(self)
        self.num_workers = num_workers
        self.start_workers()

    def add_task(self, worker_type, data):
        self.put((worker_type, data))

    def start_workers(self):
        for i in range(self.num_workers):
            t = Thread(target=self.worker)
            t.daemon = True
            t.start()

    def worker(self):
        while True:
            worker_type, data = self.get(True)
            if worker_type is AgentWorkerType.androidmonkey.value:
                logger.info('android monkey-------task id:' + str(data))
                AndroidMonkey(data).run()
                self.task_done()

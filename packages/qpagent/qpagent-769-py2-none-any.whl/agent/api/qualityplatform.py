#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.qualityplatform.api
    ~~~~~~~~~~~~

    This module provide the server api.

    :copyright: (c) 2017 by Ma Fei.
"""
import json
import logging

import requests
import time

from agent.consts import DeviceStatus
from agent.consts import TestRunStatus
from agent.util.tools import AppToolKit, HostToolKit

logger = logging.getLogger(__name__)

app_tool_kit = AppToolKit()

host_tool_kit = HostToolKit()


class QualityPlatform(object):
    def __init__(self):
        self.base_uri = 'http://qp.alta.elenet.me/api/'
        self.port = 9099
        self.session = requests.session()
        self.session.headers.update(
            dict(Token='53a308a3-93ad-11e7-9876-28cfe91a6a05'))

    def _get_url(self, path, query_params):
        query = ''
        if query_params is not None:
            query = '?'
            for k, v in query_params.iteritems():
                query += '{}={}&'.format(k, v)
            query = query[:-1]
        return self.base_uri + path + query

    def _get(self, path, **query_params):
        try:
            r = self.session.get(self._get_url(path, query_params))
            if not r.ok:
                raise Exception(repr(r))
            return r.json()
        except requests.RequestException as e:
            logger.error(e.message, exe_info=True)
            raise

    def _post(self, path, data, **query_params):
        try:
            r = self.session.post(
                self._get_url(path, query_params), json=data)
            if not r.ok:
                raise Exception(repr(r))
            return r.json()
        except requests.RequestException as e:
            logger.error(e.message, exe_info=True)
            raise

    def _upload(self, path, files, data, **query_params):
        try:
            r = self.session.post(self._get_url(path, query_params), files=files, data=data)
            if not r.ok:
                raise Exception(repr(r))
            return r.json()
        except requests.RequestException as e:
            logger.error(e.message, exe_info=True)
            raise

    def _put(self, path, data, **query_params):
        try:
            self.session.put(self._get_url(path, query_params), json=data)
        except requests.RequestException as e:
            logger.error(e.message, exe_info=True)
            raise

    def _delete(self, path, **query_params):
        try:
            self.session.delete(self._get_url(path, query_params))
        except requests.RequestException as e:
            logger.error(e.message, exe_info=True)
            raise

    def register_agent(self, status):
        devices = []
        android_devices = app_tool_kit.get_android_devices()
        for android_device in android_devices:
            device = {
                'brand': android_device.get('brand'),
                'model': android_device.get('model'),
                'os_type': android_device.get('os_type'),
                'os_version': android_device.get('os_version'),
                'rom_version': android_device.get('rom_version'),
                'uid': android_device.get('uid'),
                'status': DeviceStatus.online.value
            }
            devices.append(device)
        ios_devices = app_tool_kit.get_ios_devices()
        for ios_device in ios_devices:
            device = {
                'brand': ios_device.get('brand'),
                'model': ios_device.get('model'),
                'os_type': ios_device.get('os_type'),
                'os_version': ios_device.get('os_version'),
                'rom_version': ios_device.get('rom_version'),
                'uid': ios_device.get('uid'),
                'status': DeviceStatus.online.value
            }
            devices.append(device)
        agent_device = {
            'ip': host_tool_kit.ip(),
            'port': self.port,
            'name': host_tool_kit.name(),
            'status': status,
            'devices': devices
        }
        return self._post('agents/register', agent_device)

    def unregister_agent(self, agent_id):
        self._delete('agents/{}/unregister'.format(agent_id))

    # def update_device_status(self, device_id, status):
    #     data = {
    #         'status': status
    #     }
    #     self._put('devices/'.format(device_id), data)

    def add_case_file(self, test_case_id, case_url):
        data = {
            'url': case_url
        }
        self._put('testcases/'.format(test_case_id), data)

    def upload_file(self, case_file):
        files = {
            'file': case_file
        }
        data = {
            'extension': 'js'
        }
        return self._upload('file/upload', files, data)

    def upload_case_file(self, test_case_id, case_file):
        fuss_hash = self.upload_file(case_file)
        self.add_case_file(test_case_id, fuss_hash)

    def get_task_by_id(self, task_id):
        return self._get('tasks/{}'.format(task_id))

    def update_task_status(self, task_id, status):
        data = {
            'status': status,
        }
        self._put('tasks/{}'.format(task_id), data)

    def update_compatibility_user_status(self, name, status):
        data = {
            'name': name,
            'status': status
        }
        self._put('CT_users', data)

    def upload_task_reports(self, task_id, report):
        data = {
            'log': report,
        }
        self._put('tasks/{}'.format(task_id), data)

    def send_mail(self, receivers, title, subject, app, content, template):
        if type(receivers) is not list:
            receivers = [receivers]
        mail_content = {
            'receivers': receivers,
            'title': title,
            'subject': subject,
            'app_version': app['appVersion'],
            'commit_id': app['commitId'],
            'build_no': app['buildNo'],
            'date': time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time())),
            'aut': app['downloadURL'],
            'content': content,
            'template': template,
        }
        return self._post('mail', mail_content)

    def add_user_comment(self, user_comment):
        return self._post('comments', user_comment)

    def get_app_channel_crawler_history(self, app_channel_id):
        return self._get('crawler_histories?app_channel_id=%s' % app_channel_id)

    def add_crawler_history(self, crawler_history):
        return self._post("crawler_histories", crawler_history)

    def add_report(self, reports):
        return self._post('reports', reports)

    def add_stability_report(self, app_version, aut, log, app_id, status, os_type, device, source, uid, package_type):
        data = {
            "app_version": app_version,
            "aut": aut,
            "log": log,
            "app_id": app_id,
            "status": status,
            "os_type": os_type,
            "device": device,
            "source": source,
            "device_id": uid,
            "package_type": package_type,
        }
        return self._post('stability/report', data)

    def add_project_run(self, project_id, test_run):
        return self._post('testrail/projects/{}/runs'.format(project_id), test_run)

    def update_device_status(self, uid, row_id):
        data = {
            'uid': uid,
            'task_type': 5,
            'status': 0,
            'row_id': row_id
        }
        return self._post('devices/use', data)

    def add_results_for_cases(self, run_id, case_id, log, device, status=TestRunStatus.passed.value, app=None):
        if app:
            comment = {
                "app_version": app['appVersion'],
                "download_url": app['downloadURL'],
                "log": log,
                "device": device,
                "package_type": app['packageType'],
                "date": time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time())),
            }
        else:
            comment = {
                "log": log,
                "date": time.strftime('%Y-%m-%d  %H:%M', time.localtime(time.time())),
            }

        test_results = {
            'results': [
                {
                    "case_id": case_id,
                    "status_id": status,
                    "comment": json.dumps(comment)
                }
            ]
        }
        return self._post('testrail/test_results/runs/{}'.format(run_id), test_results)

    def get_project_milestones(self, project_id):
        return self._get('testrail/projects/{}/milestones'.format(project_id))

    def get_task_data(self, body):
        agent_task = json.load(body)
        task_id = agent_task.get('task_id')
        task_data = self.get_task_by_id(task_id)
        worker_data = json.loads(task_data.get('params'))
        worker_type = worker_data.get('worker_type')
        return task_id, worker_type

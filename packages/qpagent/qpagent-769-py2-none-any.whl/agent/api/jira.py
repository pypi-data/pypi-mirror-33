#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class JiraClient(object):
    def __init__(self):
        self.base_uri = 'http://jira.ele.to:8088/rest/api/'
        self.session = requests.session()
        self.session.auth = HTTPBasicAuth('waimai', 'waimai@123')

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

    def _get_url(self, path, query_params):
        query = ''
        if query_params is not None:
            query = '?'
            for k, v in query_params.iteritems():
                query += '{}={}&'.format(k, v)
            query = query[:-1]
        return self.base_uri + path + query

    def add_jira_issue(self, project_key, summary, description):
        issue = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": "Bug"
                }
            }
        }
        return self._post('2/issue/', issue)

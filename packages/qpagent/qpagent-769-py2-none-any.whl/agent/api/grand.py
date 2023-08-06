#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import requests

logger = logging.getLogger(__name__)


class GrandClient(object):
    def __init__(self):
        self.base_uri = 'http://mtci.beta.elenet.me:8080/ci/openapi/'
        self.session = requests.session()

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

    def get_latest_app(self, app_id, platform, pack_type, version=None):
        if version:
            return self._get('v1/builds/latest', appId=app_id, platform=platform, packType=pack_type, version=version)
        else:
            return self._get('v1/builds/latest', appId=app_id, platform=platform, packType=pack_type)

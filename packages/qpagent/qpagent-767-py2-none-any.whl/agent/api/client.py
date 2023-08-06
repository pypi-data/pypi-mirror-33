#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

import requests

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self):
        self.base_uri = 'http://qp.alta.elenet.me/api/'
        self.session = requests.session()
        self.session.headers.update(
            dict(Token='53a308a3-93ad-11e7-9876-28cfe91a6a05'))

    def _get(self, path, **query_params):
        try:
            r = self.session.get(self._get_url(path, query_params))
            if not r.ok:
                raise Exception(repr(r))
            return r.json()
        except requests.RequestException as e:
            logger.exception(e)
            raise

    def _post(self, path, data, **query_params):
        try:
            r = self.session.post(
                self._get_url(path, query_params), data=data)
            if not r.ok:
                raise Exception(repr(r))
            return r.json()
        except requests.RequestException as e:
            logger.exception(e)
            raise

    def _get_url(self, path, query_params):
        query = ''
        if query_params is not None:
            query = '?'
            for k, v in query_params.iteritems():
                query += '{}={}&'.format(k, v)
            query = query[:-1]
        return self.base_uri + path + query

    def get_channels(self, **kwargs):
        return self._get('channels', **kwargs)

    def get_channel_by_id(self, id):
        return self._get('channels/' + id)

    def get_app_channel(self, **kwargs):
        return self._get('apps/channels', **kwargs)

    def get_tasks(self, page_size=1, page_num=1, **kwargs):
        return self._get(
            'tasks',
            page_size=page_size,
            page_num=page_num,
            **kwargs)

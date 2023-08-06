#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from agent.api.grand import GrandClient


class TestGrandApi(unittest.TestCase):
    def test_get_grand_app(self):
        grand_client = GrandClient()
        print grand_client.get_latest_app('me.ele', 'Android', 'Release')
        self.assertIsNotNone(grand_client.get_latest_app('me.ele', 'Android', 'Release'))


if __name__ == '__main__':
    unittest.main()

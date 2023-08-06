#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from agent.util.tools import AppToolKit, HostToolKit

app_tool_kit = AppToolKit()

host_tool_kit = HostToolKit()


class TestAppToolKit(unittest.TestCase):
    def test_get_android_devices(self):
        print(app_tool_kit.get_android_devices())
        self.assertIsNotNone(app_tool_kit.get_android_devices())

    def test_get_ios_devices(self):
        print(app_tool_kit.get_ios_devices())
        self.assertIsNotNone(app_tool_kit.get_ios_devices())

    def test_ip(self):
        self.assertIsNotNone(host_tool_kit.ip())

    def test_name(self):
        self.assertIsNotNone(host_tool_kit.name())


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.constant
    ~~~~~~~~~~~~

    This module contains the constant.

    :copyright: (c) 2017 by Ma Fei.
"""
import enum


class AgentWorkerType(enum.IntEnum):
    unknown = 0
    macaca = 1
    selenium = 2
    appcrawler = 3
    androidmonkey = 4
    iosmonkey = 5
    crawler = 6
    resetuser = 7


class DeviceStatus(enum.IntEnum):
    online = 1
    offline = 0
    busy = 2


class TaskStatus(enum.IntEnum):
    created = 0
    running = 1
    success = 2
    failed = 3
    timeout = 4


class CompatibilityUserStatus(enum.IntEnum):
    unavailable = 0
    available = 1


class AgentStatus(enum.IntEnum):
    online = 1
    offline = 0


class TestRunStatus(enum.IntEnum):
    passed = 1
    blocked = 2
    untested = 3
    retest = 4
    failed = 5


class TestPlatform(enum.IntEnum):
    testin = 0
    aliyun = 1

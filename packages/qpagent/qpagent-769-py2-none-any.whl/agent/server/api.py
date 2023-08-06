#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.server.api
    ~~~~~~~~~~~

    This module provide the agent server api.

    :copyright: (c) 2017 by Ma Fei.
"""
import commands
import json
import logging

import bottle
import requests
from bottle import request, run, post, get, redirect

from agent.api.qualityplatform import QualityPlatform
from agent.manager import TaskQueue
from agent.util.tools import HostToolKit, AppToolKit
from agent.util.tools import PackageManage

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

q = TaskQueue(num_workers=80)

qualityplatform_client = QualityPlatform()

app = bottle.app()

host_tool_kit = HostToolKit()

app_tool = AppToolKit()

logger = logging.getLogger(__name__)


def start_server():
    run(app=app, host='', port=9099)


def stop_server():
    app.close()


@post('/jobs')
def task():
    body = request.body
    task_id, worker_type = qualityplatform_client.get_task_data(body)
    q.add_task(worker_type, task_id)


@get('/ping')
def ping():
    return json.dumps(True)


def get_ios_devices():
    cmd1 = "idevice_id -l"
    status, output = commands.getstatusoutput(cmd1)
    if len(output) > 0:
        ios_devices = output.split('\n')
    else:
        ios_devices = []
    return ios_devices


def get_android_devices():
    android_devices_list = []
    cmd1 = "adb devices"
    status, output = commands.getstatusoutput(cmd1)
    for device in output.splitlines():
        if 'device' in device and 'devices' not in device:
            device = device.split('\t')[0]
            android_devices_list.append(device)
    return android_devices_list


@get('/devices/robert')
def devices():
    if host_tool_kit.ip() != '10.12.56.7':
        return
    ios_devices = get_ios_devices()
    android_devices = get_android_devices()
    robert = []
    try:
        r = requests.get('http://10.12.56.5:9099/devices/teddy')
        if r.ok:
            robert.append(r.json())
    except requests.RequestException:
        pass

    try:
        r = requests.get('http://10.12.56.6:9099/devices/dolores')
        if r.ok:
            robert.append(r.json())
    except requests.RequestException:
        pass
    device_info = {"ios_devices": ios_devices, "android_devices": android_devices, "name": host_tool_kit.name(),
                   "ip": host_tool_kit.ip()}
    robert.append(device_info)
    return json.dumps(robert)


@get('/devices/teddy')
def devices():
    ios_devices = get_ios_devices()
    android_devices = get_android_devices()
    device_info = {"ios_devices": ios_devices, "android_devices": android_devices, "name": host_tool_kit.name(),
                   "ip": host_tool_kit.ip()}
    return device_info


@get('/devices/dolores')
def devices():
    ios_devices = get_ios_devices()
    android_devices = get_android_devices()
    device_info = {"ios_devices": ios_devices, "android_devices": android_devices, "name": host_tool_kit.name(),
                   "ip": host_tool_kit.ip()}
    return device_info


@get('/devices')
def devices():
    ios_devices = get_ios_devices()
    android_devices = get_android_devices()
    device_info = {"ios_devices": ios_devices, "android_devices": android_devices, "name": host_tool_kit.name(),
                   "ip": host_tool_kit.ip()}
    return device_info


@post('/processes')
def processes():
    arr = request.POST.allitems()
    info = ""
    for tup in arr:
        temp = ''.join(tup)
        info = info + temp

    # 对数据处理之后 存储到本地 ElementTree似乎只能处理文件。不能处理数据流
    beigin = info.find('<plist')
    end = info.find('</plist>') + 8
    xml = info[beigin:end]

    fo = open("data.xml", "wb")
    fo.write(xml)
    fo.close()

    tree = ET.ElementTree(file='data.xml')
    root = tree.getroot()
    dic = {}
    key = ""
    for child in root[0]:
        if child.tag == "key":
            key = child.text
        else:
            dic[key] = child.text
    url = "http://qp.alta.elenet.me/deviceinfo" + "?udid=" + dic["UDID"] + "&product=" + dic["PRODUCT"]
    if "SERIAL" in dic.keys():
        url = url + "&serial=" + dic["SERIAL"]
    return redirect(url, 301)


@post('/api/resetEnvi')
def resetenvi():
    body = request.body
    agent_task = json.load(body)
    udid = agent_task.get('UDID')
    packtype = agent_task.get('packtype')
    udids = AppToolKit.get_ios_deviceudid()
    if udid in udids:
        package_manage = PackageManage()
        package_manage.packtype = packtype
        package_manage.uninstall_app(udid)  # 卸载
        package_manage.install_localapp(udid)  # 安装
    return json.dumps(True)

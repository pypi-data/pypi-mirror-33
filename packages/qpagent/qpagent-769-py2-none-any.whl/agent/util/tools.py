#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.util.tools
    ~~~~~~~~~~~~

    This module provide the tool.

    :copyright: (c) 2017 by Ma Fei.
"""
import commands
import logging
import os
import socket
import urllib2
from ftplib import FTP

import datetime
import requests
import sys
import time
from apptoolkit import Device, Shell

from agent.exc import AgentException

# iOS 中对应的表
ios_translate_map = {"iPhone3,1": "iPhone4(GSM)", "iPad1,1": "iPad", "iPod2,1": "iPodTouch2G", "AppleTV5,3": "AppleTV",
                     "iPhone6,1": "iPhone5s", "iPhone3,3": "iPhone4(CDMA)", "iPhone6,2": "iPhone5s",
                     "iPhone9,1": "iPhone7(A1660\/A1779\/A1780)", "iPhone9,2": "iPhone7Plus(A1661\/A1785\/A1786)",
                     "iPad2,1": "iPad2(WiFi)", "iPad2,2": "iPad2(GSM)", "iPod3,1": "iPodTouch3G",
                     "iPad2,3": "iPad2(CDMA)", "iPhone9,3": "iPhone7(A1778)", "iPad2,4": "iPad2(WiFi)",
                     "iPad2,5": "iPadMini(WiFi)", "iPhone9,4": "iPhone7Plus(A1784)", "iPad2,6": "iPadMini(GSM)",
                     "iPad2,7": "iPadMini(CDMA)", "iPhone1,1": "iPhone1G", "iPad3,1": "iPad3(WiFi)",
                     "iPod4,1": "iPodTouch4G", "iPad3,2": "iPad3(CDMA)", "iPhone1,2": "iPhone3G",
                     "iPad3,3": "iPad3(GSM)", "iPhone4,1": "iPhone4S", "iPad3,4": "iPad4(WiFi)",
                     "iPad3,5": "iPad4(GSM)", "iPad3,6": "iPad4(CDMA)", "iPhone7,1": "iPhone6Plus",
                     "iPad4,1": "iPadAir(WiFi)", "iPhone7,2": "iPhone6", "iPad4,2": "iPadAir(GSM)",
                     "iPod5,1": "iPodTouch5G", "iPad4,3": "iPadAir(CDMA)", "iPad4,4": "iPadMiniRetina(WiFi)",
                     "iPad4,5": "iPadMiniRetina(Cellular)", "iPad4,7": "iPadMini3(WiFi)",
                     "iPad4,8": "iPadMini3(Cellular)", "iPad4,9": "iPadMini3(Cellular)", "iPad5,1": "iPadMini4(WiFi)",
                     "iPad5,2": "iPadMini4(Cellular)", "iPad5,3": "iPadAir2(WiFi)", "iPad5,4": "iPadAir2(Cellular)",
                     "iPhone2,1": "iPhone3GS", "iPhone5,1": "iPhone5(GSM)", "iPod7,1": "iPodTouch6G",
                     "iPhone5,2": "iPhone5(CDMA)", "iPad6,3": "iPadPro9.7-inch(WiFi)", "iPhone8,1": "iPhone6s",
                     "iPad6,4": "iPadPro9.7-inch(Cellular)", "iPhone5,3": "iPhone5c", "i386,x86_64": "Simulator",
                     "iPhone8,2": "iPhone6sPlus", "iPhone5,4": "iPhone5c", "iPad6,7": "iPadPro12.9-inch(WiFi)",
                     "iPad6,8": "iPadPro12.9-inch(Cellular)", "iPod1,1": "iPodTouch1G", "iPhone8,4": "iPhoneSE",
                     "iPhone10,1": "iPhone8",
                     "iPhone10,2": "iPhone8Plus",
                     "iPhone10,3": "iPhoneX",
                     "iPhone10,4": "iPhone8",
                     "iPhone10,5": "iPhone8Plus",
                     "iPhone10,6": "iPhoneX",
                     "iPad7,1": "iPad Pro(12.9-inch)",
                     "iPad7,2": "iPad Pro(12.9-inch)",
                     "iPad7,3": "iPad Pro(10.5-inch)",
                     "iPad7,4": "iPad Pro(10.5-inch)"}

logger = logging.getLogger(__name__)


def check_new_user(user_id='', phone='', device_id=''):
    base_url = 'https://sakura.alpha.elenet.me/api/qa_tools/users/check_new'
    where_params = "{\"user_id\":\"" + user_id + "\",\"phone\":\"" + phone + "\",\"device_id\":\"" + device_id + "\"}"
    params = {
        'limit': 10,
        'offset': 0,
        'where': where_params
    }
    resp = requests.get(base_url, params=params, timeout=10)
    if resp.status_code == 200:
        return resp.json()[0].get('is_new_user')
    else:
        raise Exception("check new user failed")


class AppToolKit(object):
    @staticmethod
    def get_android_devices():
        return Device.get_android_devices()

    @staticmethod
    def get_android_device_name(device_uid):
        from apptoolkit import ADB
        adb = ADB(device_uid)
        return adb.get_product_brand() + " " + adb.get_product_model()

    @staticmethod
    def install_android_app(devices, app):
        cmd = "adb -s " + devices + " install -r " + app
        logger.info(cmd)
        Shell.invoke(cmd)

    @staticmethod
    def uninstall_android_app(devices, app):
        cmd = "adb -s " + devices + " shell pm uninstall  " + app
        logger.info(cmd)
        Shell.invoke(cmd)

    @staticmethod
    def get_ios_devices():
        return Device.get_ios_devices()

    @staticmethod
    def unlock(device_id):
        cmd = 'adb -s %s shell am start -n com.android.jarvis/.Unlock' % device_id
        logger.info(cmd)
        Shell.invoke(cmd)

    @staticmethod
    def enable_wifi(device_id):
        cmd = 'adb -s %s shell am start -n com.android.jarvis/.Wifi' % device_id
        logger.info(cmd)
        Shell.invoke(cmd)

    @staticmethod
    def open_status_bar(device_id):
        cmd = 'adb -s %s shell am broadcast -a com.android.jarvis.SET_OVERLAY --ez enable true' % device_id
        logger.info(cmd)
        Shell.invoke(cmd)

    @staticmethod
    def close_status_bar(device_id):
        cmd = 'adb -s %s shell am broadcast -a com.android.jarvis.SET_OVERLAY --ez enable false' % device_id
        logger.info(cmd)
        Shell.invoke(cmd)

    # 获取连接上USB的手机的udid列表
    @staticmethod
    def get_ios_deviceudid():
        udid_cmd = "idevice_id -l"
        status, output = commands.getstatusoutput(udid_cmd)
        if len(output) > 0:
            udids = output.split('\n')
            return udids
        return []

    # 通过udid获取手机名字
    @staticmethod
    def get_ios_devicename(udid):
        cmd = "ideviceinfo -u %s -k DeviceName" % udid
        status, output = commands.getstatusoutput(cmd)
        return output

    # 通过udid获取手机型号
    @staticmethod
    def get_ios_devicemodel(udid):
        cmd = "ideviceinfo -u %s -k ProductType" % udid
        status, output = commands.getstatusoutput(cmd)
        device_type = ios_translate_map[output]
        return device_type

    # 通过udid获取手机类型（iPhone/iPad/iPod）
    @staticmethod
    def get_ios_devicebrand(udid):
        device_type = AppToolKit.get_ios_devicemodel(udid)
        brand = ''
        # -1表示找不到 0表示下标
        if device_type.find("iPhone") != -1:
            brand = 'iPhone'
        elif device_type.find("iPad") != -1:
            brand = 'iPad'
        elif device_type.find("iPod") != -1:
            brand = 'iPod'
        return brand

    # 通过udid获取手机版本
    @staticmethod
    def get_ios_deviceversion(udid):
        cmd = "ideviceinfo -u %s -k ProductVersion" % udid
        status, output = commands.getstatusoutput(cmd)
        return output


class STF(object):
    @staticmethod
    def add_user_device(device_uid):
        data = '{"serial":"' + device_uid + '","timeout": 90000000000000}'
        cmd = "curl -X POST --header 'Content-Type: application/json' --data '" + data + \
              "' -H 'Authorization: Bearer f0c50aedaaa245618eaa552e962d1b1d3bd07f3c17a8429b902519de29268979' " \
              "http://10.12.53.34:7100/api/v1/user/devices"
        Shell.invoke(cmd)

    @staticmethod
    def delete_user_device(device_uid):
        cmd = 'curl -X DELETE -H "Authorization: Bearer ' \
              'f0c50aedaaa245618eaa552e962d1b1d3bd07f3c17a8429b902519de29268979" ' \
              'http://10.12.53.34:7100/api/v1/user/devices/{%s}' % device_uid
        Shell.invoke(cmd)


class HostToolKit(object):
    @staticmethod
    def ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            _ip = s.getsockname()[0]
        except Exception as e:
            raise AgentException(e)
        finally:
            s.close()

        return _ip

    @staticmethod
    def name():
        return socket.gethostname()


class FileToolKit(object):
    def __init__(self):
        pass

    @staticmethod
    def __get_download_url(url):
        """
        获取跳转后的真实下载链接
        :param url: 页面中的下载链接
        :return: 跳转后的真实下载链接
        """
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
        response = urllib2.urlopen(req)
        dlurl = response.geturl()  # 跳转后的真实下载链接
        return dlurl

    @staticmethod
    def __download_file(dlurl):
        """
        从真实的下载链接下载文件
        :param dlurl: 真实的下载链接
        :return: 下载后的文件
        """
        req = urllib2.Request(dlurl)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko')
        response = urllib2.urlopen(req)
        return response

    def save_file(self, dlurl, dlfolder, filename, progress=False):
        """
        把下载后的文件保存到下载目录
        :param progress:
        :param filename:
        :param dlurl: 真实的下载链接
        :param dlfolder: 下载目录
        :return: NoneTrue
        """
        if os.path.isdir(dlfolder):
            pass
        else:
            os.makedirs(dlfolder)
        os.chdir(dlfolder)  # 跳转到下载目录
        # filename = dlurl.split('/')[-1]  # 获取下载文件名
        response = self.__download_file(dlurl)
        if progress:
            self.__chunk_read(response, filename, report_hook=self.__chunk_report)
        dlfile = response.read()
        with open(filename, 'wb') as f:
            f.write(dlfile)
            f.close()
        return None

    @staticmethod
    def make_worker_dir(path):
        if os.path.isdir(path):
            pass
        else:
            os.makedirs(path)
        return path

    @staticmethod
    def __chunk_report(bytes_so_far, total_size, filename):
        percent = float(bytes_so_far) / total_size
        percent = round(percent * 100, 2)
        print ("Downloaded %s %d of %d bytes (%0.2f%%)\r" %
               (filename, bytes_so_far, total_size, percent))
        if bytes_so_far >= total_size:
            print '\n'

    @staticmethod
    def __chunk_read(response, filename, chunk_size=8192, report_hook=None):
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0
        now = datetime.datetime.now()
        while 1:
            chunk = response.read(chunk_size)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            now2 = datetime.datetime.now()
            if (now2 - now).seconds > 3 and report_hook:
                now = now2
                report_hook(bytes_so_far, total_size, filename)

        return bytes_so_far


class FTPToolKit(object):
    def __init__(self):
        self.ftp = None
        self.ip = '172.16.94.6'
        self.uname = 'administrator'
        self.pwd = 'eleme517517'
        self.port = 21
        self.timeout = 60

    def init_env(self):
        if self.ftp is None:
            self.ftp = FTP()
            print '### connect ftp server: %s ...' % self.ip
            self.ftp.connect(self.ip, self.port, self.timeout)
            self.ftp.login(self.uname, self.pwd)
            print self.ftp.getwelcome()

    def clear_env(self):
        if self.ftp:
            self.ftp.close()
            print '### disconnect ftp server: %s!' % self.ip
            self.ftp = None

    def upload_dir(self, localdir='./', remotedir='./'):
        if not os.path.isdir(localdir):
            return
        self.ftp.cwd(remotedir)
        for file in os.listdir(localdir):
            src = os.path.join(localdir, file)
            if os.path.isfile(src):
                self.upload_file(src, file)
            elif os.path.isdir(src):
                try:
                    self.ftp.mkd(file)
                except Exception:
                    sys.stderr.write('the dir is exists %s' % file)
                self.upload_dir(src, file)
        self.ftp.cwd('..')

    def upload_file(self, localpath, remotepath='./'):
        if not os.path.isfile(localpath):
            return
        print '+++ upload %s to %s:%s' % (localpath, self.ip, remotepath)
        self.ftp.storbinary('STOR ' + remotepath, open(localpath, 'rb'))

    def upload(self, localdir, remotedir):
        print(localdir)
        print(remotedir)
        self.init_env()
        try:
            self.ftp.mkd(remotedir)
        except Exception as e:
            print(e.message)
        self.upload_dir(localdir, remotedir)
        self.clear_env()


class PackageManage(object):
    def __init__(self, resign=True):
        self.dir = os.path.dirname(__file__)
        self.workdir = os.environ['HOME'] + "/"

        if resign:
            self.localdevapp = self.workdir + "agent/iospackage/resigndevelop.ipa"
            self.localrelapp = self.workdir + "agent/iospackage/resignrelease.ipa"
            self.qpagent_bundleid = 'me.ele.ios.qpagent'
        else:
            self.localdevapp = self.workdir + "agent/iospackage/develop.ipa"
            self.localrelapp = self.workdir + "agent/iospackage/release.ipa"
            self.qpagent_bundleid = 'me.ele.ios.eleme'
        self.packtype = "Debug"

        # todo 暂时所有的操作是使用重签名的包和bundleID，即所有的操作使用重签名之后的包。后期更新
        self.bundleId = self.qpagent_bundleid

    def install_localapp(self, udid):
        if self.packtype == "Debug":
            resigned_ipa = self.localdevapp
        else:
            resigned_ipa = self.localrelapp

        install_cmd = "ideviceinstaller -u %s -i %s" % (udid, resigned_ipa)
        logging.info(" install app :" + install_cmd)
        commands.getstatusoutput(install_cmd)
        # 经常会出现 过了很久 包没有安装上的情况
        time.sleep(20)

    def uninstall_app(self, udid):
        uninstall_cmd = "ideviceinstaller -u %s -U %s" % (udid, self.bundleId)
        logging.info(" uninstall app :" + uninstall_cmd)
        commands.getstatusoutput(uninstall_cmd)


from sys import argv
import os
import platform

from .configurations import SweetPySettings
from .const import *
from django.conf import settings
import socket

#执行模式获取
if 'uwsgi' in argv:
    SweetPySettings.RunMode = RunModeConst.UWSGIMode
else:
    if 'runserver' in argv:
        if os.environ.get("RUN_MAIN",None) == "true":
            SweetPySettings.RunMode = RunModeConst.PythonModeChinldren
        else:
            SweetPySettings.RunMode = RunModeConst.PythonModeParent
    elif 'test' in argv:
        SweetPySettings.RunMode = RunModeConst.PythonModeTest
    else:
        SweetPySettings.RunMode = RunModeConst.PythonModeOther

#操作系统获取
sysstr = platform.system()
if sysstr.lower() == 'windows':
    SweetPySettings.OperatingSystem = OperatingSystemConst.Windows
else:
    SweetPySettings.OperatingSystem = OperatingSystemConst.Linux


#获取配置文件目录
def get_dirs_name_by_path(path):
    result = []
    for dirpath, dirnames, filenames in os.walk(path):
        for dir in dirnames:
            result.append(dir)
        break
    return result
def get_project_setting_path():
    local_path = os.getcwd()
    dirs = get_dirs_name_by_path(local_path)
    for _dir in dirs:
        if SweetPySettings.OperatingSystem == OperatingSystemConst.Windows:
            filename = local_path + '\\' + _dir + '\\wsgi.py'
            if os.path.exists(filename):
                return _dir
        else:
            filename = local_path + '/' + _dir + '/wsgi.py'
            if os.path.exists(filename):
                return _dir
    return ''
SweetPySettings.SettingsFilePath = get_project_setting_path()

#获取本机IP
def get_local_ip():
    ip = '127.0.0.1'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

SweetPySettings.LocalIP = get_local_ip()



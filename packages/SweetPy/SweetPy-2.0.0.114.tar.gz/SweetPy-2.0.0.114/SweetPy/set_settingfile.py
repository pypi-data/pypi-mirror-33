import os
from sys import argv
from .configurations import SweetPySettings
from .const import *


def set_environ():
    if SweetPySettings.RunMode ==  RunModeConst.UWSGIMode:
        setting_filename = SweetPySettings.SettingsFilePath + ".settings_production"
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", setting_filename)
        print('SeetPy启动[uwsgi]配置文件[' + setting_filename + ']...')
    else:
        sweetpy_env_file = os.environ.get('SWEETPY_ENV_PRODUCTION_SETTING_FILE', None)
        if sweetpy_env_file:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", sweetpy_env_file)
            print('SeetPy启动配置文件[' + sweetpy_env_file + ']...')
        else:
            setting_filename = ''
            for _file in argv:
                if _file.startswith('settingfile_'):
                    setting_filename = _file
                    break
            if setting_filename:
                _filename = setting_filename.replace('settingfile_','')
                module_name = SweetPySettings.SettingsFilePath + "." + _filename
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", module_name)
                os.environ.setdefault("SWEETPY_ENV_PRODUCTION_SETTING_FILE", module_name)
                argv.remove(setting_filename)
                print('SeetPy启动配置文件[' + module_name + ']...')
            else:
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", SweetPySettings.SettingsFilePath + ".settings")
                print('SeetPy启动默认配置文件...')

set_environ()
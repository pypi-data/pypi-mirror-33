print('检查是否注册应用云...')
import requests
import json
from django.conf import settings
from .configurations import SweetPySettings

def cloudsetting_to_djangosetting(params):
    if params:
        try:
            for _params in params.keys():
                params_name_upper = _params.upper()
                params_name_upper = params_name_upper.replace('.','_')
                setattr(settings,params_name_upper,params.get(_params,None))
        except Exception as e:
            print('cloudsetting_to_djangosetting err ' + str(e))

if (hasattr(settings, 'SWEET_CLOUD_ENABLED')) and settings.SWEET_CLOUD_ENABLED:
    url = settings.SWEET_CLOUD_JOINT_URL + '?' + \
          'application=' + settings.SWEET_CLOUD_APPNAME + \
          '&index=' + settings.SWEET_CLOUD_APPPORT + \
          '&version=' + settings.SWEET_CLOUD_VERSION + \
          '&ticket=' + settings.SWEET_CLOUD_TICKET

    try:
        re_connect = 10
        while re_connect > 0:
            result = requests.get(url)
            result_dict = json.loads(result.text)
            if result_dict['code'] == 'success':
                SweetPySettings.CloudSettings = result_dict['data']
                SweetPySettings.IsCloudConnected = True
                cloudsetting_to_djangosetting(SweetPySettings.CloudSettings.get('applicationInstanceConfigurations',None))
                print('应用云连接成功...')
                re_connect = -1
            else:
                print('应用云连接失败:' + result_dict['message'])
                re_connect -= 1
                print('等待一秒重试...')
                import time
                time.sleep(1)
        if re_connect == 0:
            quit(0)
    except Exception as e:
        print("无法连接到应用云,请检查配置是否正确!")
        quit(0)
else:
    print('程序配置不连接应用云!')

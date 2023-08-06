print('设置数据库连接器参数(应用云配置)...')

from django.conf import settings
from .configurations import SweetPySettings


def db_connect(sweet_settings = None):
    if sweet_settings['applicationInstanceConfigurations'].get('spring.datasource.db-type', None) == None:
        return
    default = None
    try:
        _driver_name = sweet_settings['applicationInstanceConfigurations']['spring.datasource.db-type'].lower()
        _url = sweet_settings['applicationInstanceConfigurations']['spring.datasource.url']
        if _url.find(':') != -1:
            _ip = _url[:_url.find(':')]
            _port = _url[_url.find(':') + 1:]
        if _driver_name == 'postgres':
            default = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': sweet_settings['applicationInstanceConfigurations']['spring.datasource.name'],
                'USER': sweet_settings['applicationInstanceConfigurations']['spring.datasource.username'],
                'PASSWORD': sweet_settings['applicationInstanceConfigurations']['spring.datasource.password'],
                'HOST': _ip,
                'PORT': _port,
                'CONN_MAX_AGE': int(sweet_settings['applicationInstanceConfigurations']['spring.datasource.maxActive'])
            }
        elif _driver_name == 'mysql':
            default = {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': sweet_settings['applicationInstanceConfigurations']['spring.datasource.name'],
                'USER': sweet_settings['applicationInstanceConfigurations']['spring.datasource.username'],
                'PASSWORD': sweet_settings['applicationInstanceConfigurations']['spring.datasource.password'],
                'HOST': _ip,
                'PORT': _port,
                'CONN_MAX_AGE': int(sweet_settings['applicationInstanceConfigurations']['spring.datasource.maxActive'])
            }
        elif _driver_name == 'sqlite':
            default = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': _url,
            }
        if default:
            settings.DATABASES['default'] = default
    except Exception as e:
        print("数据配置错误,请配置以下字段:["
              "'spring.datasource.db-type':'数据库类型postgres,mysql,sqlite等',"
              "'spring.datasource.username':'用户名',"
              "'spring.datasource.password':'密码',"
              "'spring.datasource.url':'IP地址和端口号以:号分隔',"
              "'spring.datasource.maxActive':'连接池大小',"
              "'spring.datasource.name':'要连接的仓库名',"
              "'spring.datasource.minIdle':'连接池回收时间(暂时未启用)']")
        quit(0)

if SweetPySettings.CloudSettings:
    db_connect(SweetPySettings.CloudSettings)
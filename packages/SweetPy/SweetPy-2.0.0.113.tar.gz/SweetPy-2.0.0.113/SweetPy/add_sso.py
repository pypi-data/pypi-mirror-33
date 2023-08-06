print('注册sso组件...')

from .configurations import SweetPySettings
from django.conf import settings

if SweetPySettings.CloudSettings:
    sweet_settings = SweetPySettings.CloudSettings
    if sweet_settings:
        sso_url = sweet_settings['applicationInstanceConfigurations'].get('sweet.sso.url',None)
        if sso_url:
            from .geely_auth.geely_sso import anon_geely_sso_login
            anon_geely_sso_login.sso_url = sso_url
            settings.LOGIN_URL = '/anon/geely-sso/login'
            settings.LOGOUT_URL = '/anon/geely-sso/logout'
            settings.AUTH_PROFILE_MODULE = 'SweetPy.geely_auth.Employee'
        sso_token = sweet_settings['applicationInstanceConfigurations'].get('sweet.sso.token.url',None)
        if sso_token:
            from .geely_auth.geely_sso import anon_geely_sso,anon_geely_sso_logout
            anon_geely_sso.sso_token_url = anon_geely_sso_logout.sso_token_url = sso_token
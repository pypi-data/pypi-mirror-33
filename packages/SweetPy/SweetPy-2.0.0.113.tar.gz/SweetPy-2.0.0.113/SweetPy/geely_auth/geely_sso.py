print('注册本地用户跳转信息...')

from rest_framework.views import APIView
import requests
from django.http import HttpResponseRedirect
from SweetPy.func_plus import FuncHelper
from ..extend.response_plus import APIResponseHTTPCode, create_response
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login


def get_login_url(request):
    from SweetPy.configurations import SweetPySettings
    url = SweetPySettings.CloudSettings['applicationInstanceConfigurations'].get('sweet.sso.url', None)
    appkey = SweetPySettings.CloudSettings['applicationInstanceConfigurations'].get('sweet.sso.appkey', None)
    if url is None:
        return None
    _host = request.get_host()
    redirect_url = 'http://' + _host + '{path}&appKey=' + appkey
    url += '?redirectUrl=' + redirect_url
    return url

def get_user_info_by_ssotoken(ticket):
    from SweetPy.configurations import SweetPySettings
    ip = SweetPySettings.CloudSettings['applicationInstanceConfigurations'].get('sweet.sso.rest.url', None)
    appkey = SweetPySettings.CloudSettings['applicationInstanceConfigurations'].get('sweet.sso.appkey', None)
    try:
        result = requests.get(ip + 'session-info-new/' + ticket + '?appKey=' + appkey)
        json_data = FuncHelper.json_to_dict(result.text)
        if json_data['code'] == 'success':
            return json_data['data']
        else:
            return None
    except Exception as e:
        print('get_user_info_by_ssotoken err:' + str(e))
        return None

def update_expiration(ticket):
    try:
        from SweetPy.configurations import SweetPySettings
        ip = SweetPySettings.CloudSettings['applicationInstanceConfigurations'].get('sweet.sso.rest.url', None)
        result = requests.put(ip + '/expiration/' + ticket + '?expiresInMinutes=30')
        # result = req(service_name, request, 'PUT', '/expiration/' + ticket + '?expiresInMinutes=30', False)
        json_data = FuncHelper.json_to_dict(result.text)
        if json_data['code'] == 'success':
            return True
        else:
            return None
    except Exception as e:
        print('update_expiration err:' + str(e))
        return None

def logout_user(ticket):
    from SweetPy.configurations import SweetPySettings
    ip = SweetPySettings.CloudSettings['applicationInstanceConfigurations'].get('sweet.sso.rest.url', None)
    if ip is None:
        return create_response(APIResponseHTTPCode.BAD_PARAMETER)
    try:
        result = requests.get(ip + 'invalidate/' + ticket)
            # result = req(settings.SSO_SERVICE_NAME, request, 'GET', '/invalidate/' + ticket, False)
        json_data = FuncHelper.json_to_dict(result.text)
        if json_data['code'] == 'success':
            return True
        else:
            return None
    except Exception as e:
        print('get_user_info_by_ssotoken err:' + str(e))
        return None

class anon_geely_sso(APIView):
    sso_token_url = None
    def get(self, request, format=None):
        """
        登陆跳转信息
        """
        from SweetPy.extend.response_plus import APIResponseHTTPCode,create_response
        if request.GET:
            ticket = request.GET.get('ticket', None)
            redirect_url = request.GET.get('redirectUrl', None)
            if ticket:
                json_data = get_user_info_by_ssotoken(ticket)
                if json_data:
                    _userName = json_data['nickName']
                    _mobile = json_data['phone']
                    _empNo = json_data['empNo']
                    _domainAccount = json_data['domainAccountList'][0]
                    _userId = json_data['userId']

                    from django.contrib.auth.models import User
                    # user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
                    try:
                        user = User.objects.get(username=_domainAccount)
                        user.employee.ticket = ticket
                        user.employee.save()
                    except Exception as e:
                        user = None
                    authuser = None
                    if user:
                        # user.employee.chinese_name = _userName
                        authuser = authenticate(request,username=_domainAccount,password=_domainAccount)
                    else:
                        user = User.objects.create_user(_domainAccount,_domainAccount, _domainAccount)
                        from .models import Employee
                        employee = Employee()
                        employee.user = user
                        employee.chinese_name = _userName
                        employee.mobile = _mobile
                        employee.domain_account = _domainAccount
                        employee.emp_no = _empNo
                        employee.ticket = ticket
                        employee.remark = str(json_data)
                        employee.save()
                        authuser = authenticate(request, username=_domainAccount, password=_domainAccount)

                    if user is not None:
                        login(request, user)
                        request.session.set_expiry(0)
                    # user = authenticate(username='john', password='secret')

                    if redirect_url:
                        return HttpResponseRedirect(redirect_url)
                    return HttpResponseRedirect('/')
                else:
                    return create_response(APIResponseHTTPCode.FAIL, faild_message='not get user information')
            else:
                return create_response(APIResponseHTTPCode.BAD_PARAMETER)
class anon_geely_sso_login(APIView):
    '''
    登陆入口
    '''
    sso_url = None
    def get(self, request, format=None):
        redirect_url = request.query_params['next']
        url = get_login_url(request)
        if url:
            url = ''.replace('{path}',redirect_url)
        if url:
            return HttpResponseRedirect(anon_geely_sso_login.sso_url + '?redirectUrl=' + url)
        return HttpResponseRedirect('/')

class anon_geely_sso_expiration(APIView):
    '''
    更新TOKEN有效时间
    '''
    sso_token_url = None
    def get(self, request, format=None):
        ticket = None
        if hasattr(request,'user'):
            employee = request.user.employee
            ticket = employee.ticket
        if ticket:
            if update_expiration(ticket):
                return create_response(APIResponseHTTPCode.SUCCESS)
        return create_response(APIResponseHTTPCode.FAIL,'登陆可能已经失效!')

class anon_geely_sso_logout(APIView):
    '''
    退出登陆
    '''
    sso_token_url = None
    def get(self, request, format=None):
        ticket = None
        if hasattr(request, 'user'):
            employee = request.user.employee
            ticket = employee.ticket
        if ticket:
            logout_user(ticket)
        logout(request)
        return HttpResponseRedirect('/')

from django.conf import settings
if hasattr(settings,'SWEET_USER_ENABLED') and settings.SWEET_USER_ENABLED:

    from django.conf.urls import RegexURLPattern
    from django.core.checks.urls import check_resolver
    from django.core.checks.registry import register, Tags

    anon_geely_sso_regex = RegexURLPattern('^login/success$', anon_geely_sso.as_view())
    anon_geely_sso_login_regex = RegexURLPattern('^login$', anon_geely_sso_login.as_view())
    anon_geely_sso_logout_regex = RegexURLPattern('^logout$', anon_geely_sso_logout.as_view())
    anon_geely_sso_token_expiration_regex = RegexURLPattern('^login/expiration$', anon_geely_sso_expiration.as_view())

    @register(Tags.urls)
    def check_url_config(app_configs, **kwargs):
        if getattr(settings, 'ROOT_URLCONF', None):
            from django.urls import get_resolver
            resolver = get_resolver()
            resolver.url_patterns.append(anon_geely_sso_regex)
            resolver.url_patterns.append(anon_geely_sso_login_regex)
            resolver.url_patterns.append(anon_geely_sso_logout_regex)
            resolver.url_patterns.append(anon_geely_sso_token_expiration_regex)
            return check_resolver(resolver)
        return []
    import django
    django.core.checks.urls.check_url_config = check_url_config
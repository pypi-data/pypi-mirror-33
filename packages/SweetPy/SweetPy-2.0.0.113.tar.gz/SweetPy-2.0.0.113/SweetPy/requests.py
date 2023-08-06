from django.conf import settings
from .configurations import SweetPySettings
from .extend.zookeeper_plus import ZookeeperPlusWatch,ZookeeperPlus

import time
import requests
import json
import threading

class Host(object):
    app_host = None
    app_port = None

    def __init__(self,host,port):
        self.app_host = host
        self.app_port = port

class App(object):
    hosts = []
    cur_index = 0
    is_host_update = False
    is_add_watch = False

    def __init__(self,appname,zk_client):
        self.appname = appname
        self.zk_client = zk_client
        self.mutex=threading.Lock()

        if self.zk_client.exists('/realms/' + appname):
            if not self.add_node_watch('/realms/' + appname,self.update_hosts):
                print('APP[' + appname + ']zk监视线程启动失败!')

    def add_node_watch(self,node_path,func):
        result = False
        if self.zk_client == None:
            return result
        self.zpw = ZookeeperPlusWatch(self.zk_client)
        if self.zpw.add_node_watch(node_path, func):
            result = True
            self.is_add_watch = True
        return result

    def update_hosts(self,*args):
        self.mutex.acquire()
        try:
            self.hosts.clear()
            ports = args[0][0]
            if ports:
                for port in ports:
                    nodeinfo = self.zk_client.get('/realms/' + self.appname + '/' + str(port))
                    data_dict = json.loads(nodeinfo[0].decode('utf-8'))
                    host = Host(data_dict['appHost'],port)
                    self.hosts.append(host)
        finally:
            self.mutex.release()
        self.is_host_update = True

    def get_server(self):
        if not self.is_add_watch:
            if self.zk_client.exists('/realms/' + self.appname):
                if not self.add_node_watch('/realms/' + self.appname, self.update_hosts):
                    print('APP[' + self.appname + ']zk监视线程启动失败!')
                else:
                    return ''
            else:
                return ''
        while not self.is_host_update:
            time.sleep(0.1)
        self.mutex.acquire()
        try:
            if self.hosts:
                if self.cur_index >= (len(self.hosts) - 1):
                    self.cur_index = 0
                    return self.hosts[0].app_host + ':' + self.hosts[0].app_port
                else:
                    self.cur_index += 1
                    return self.hosts[self.cur_index].app_host + ':' + self.hosts[self.cur_index].app_port
            else:
                return ''
        finally:
            self.mutex.release()

class CloudApplications(object):
    apps = {}
    zk = None

    def __init__(self):
        # zk = ZookeeperPlus('10.86.96.39:2181', 'sweetCloud', 'sweetCloud123')
        sweet_settings = SweetPySettings.CloudSettings
        _zk_info = sweet_settings['zk']['zkConnectionString']
        _n_p = sweet_settings['zk']['zkDigestAuthString']
        _zk_username = _n_p[:_n_p.find(':')]
        _zk_password = _n_p[_n_p.find(':') + 1:]
        zk = ZookeeperPlus(_zk_info, _zk_username, _zk_password)
        zk.start()
        self.zk = zk

    def get_server_by_app_name(self,appname):
        if appname in self.apps.keys():
            app = self.apps.get(appname,None)
        else:
            app = App(appname,self.zk)
            self.apps[appname] = app
        return app.get_server()

cloud_appliactions = None

def request(appname,source_request,method, path, isssl,**kwargs):
    global cloud_appliactions
    if cloud_appliactions is None:
        cloud_appliactions = CloudApplications()
    serverip = cloud_appliactions.get_server_by_app_name(appname)
    if not serverip:
        print('当前查找的APP[' + appname + ']没有实例在运行中...')
        return None
    if isssl:
        url = 'https://' + serverip + path
    else:
        url = 'http://' + serverip + path
    tracker_id = None
    if source_request:
        if hasattr(source_request, 'tracker'):
            tracker = source_request.tracker
            tracker_id = tracker.tracker_id
    headers = kwargs.get('headers',None)
    if headers is None:
        headers = {}
    if tracker_id:
        headers['X-SWEET-CLOUD-TRACE-ID'] = tracker_id
    headers['X-SWEET-CLOUD-FROM'] = settings.SWEET_CLOUD_APPNAME
    headers['X-SWEET-CLOUD-FROM-INDEX'] = settings.SWEET_CLOUD_APPPORT
    headers['X-SWEET-CLOUD-TARGET'] = ''
    headers['X-SWEET-CLOUD-TARGET-VERSION'] = SweetPySettings.Version
    kwargs['headers'] = headers
    return requests.request(method, url, **kwargs)

def get_service_ip_by_service_name(service_name):
    global cloud_appliactions
    if cloud_appliactions is None:
        cloud_appliactions = CloudApplications()
    return cloud_appliactions.get_server_by_app_name(service_name)

# ####################使用方法######################
# from SweetPy.requests import request as req
# data = {}
# data['startTime'] = 'startTime'
# data['endTime'] = 'endTime'
# params = {}
# params['data'] = data
# result = req('app-cloud-log-data-analysis', request, 'GET', '/trace-log/platform/error-info', False, data=data)
# print(result.text)
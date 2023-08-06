print('注册Zookeeper状态...')

from SweetPy.extend.zookeeper_plus import ZookeeperPlus, ZookeeperPlusWatch
from .configurations import SweetPySettings
from django.conf import settings
from .const import RunModeConst

def zookeeper_on_line(sweet_settings):
    if not sweet_settings:
        return
    if not (hasattr(settings, 'SWEET_CLOUD_ENABLED') and (settings.SWEET_CLOUD_ENABLED)):
        return
    _zk_info = sweet_settings['zk']['zkConnectionString']
    _n_p = sweet_settings['zk']['zkDigestAuthString']
    _zk_username = _n_p[:_n_p.find(':')]
    _zk_password = _n_p[_n_p.find(':') + 1:]
    try:
        SweetPySettings.ZookeeperClient = ZookeeperPlus(_zk_info, _zk_username, _zk_password)
    except Exception as e:
        print('应用云状态服务器连接失败! 错误原因:' ,str(e))
        return

    zk_plus = SweetPySettings.ZookeeperClient

    app_name = settings.SWEET_CLOUD_APPNAME
    app_host = SweetPySettings.LocalIP
    app_port = settings.SWEET_CLOUD_APPPORT
    app_version = settings.SWEET_CLOUD_VERSION
    app_info_appliacations = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, SweetPySettings.Version)
    app_info_realms = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, SweetPySettings.Version,
                                                    state='Running')  # Running  Stoped
    app_runtime_data = zk_plus.create_runtime_data()

    # zk_plus.delete_app_path(app_name)

    zk_plus.set_configuration(app_name, app_port)
    zk_plus.set_dependencies(app_name, app_port)
    zk_plus.set_information(app_name, app_port, app_info_appliacations)
    zk_plus.set_metadata(app_name, app_port)
    zk_plus.set_runtime_data(app_name, app_port, app_runtime_data)
    try:
        zk_plus.set_realms(app_name, app_port, app_info_realms)
    except Exception as e:
        print('应用云状态更新失败! 错误原因:', str(e))
        return
    print('应用程序['+ app_name + ']已注册到应用云平台!')
    return True

# 如果是uwsgi程序执行到这里就直接注册  否则为修改为程序初始化完  再注册
def start_zookeeper(settings):
    import time
    time.sleep(1)
    if zookeeper_on_line(settings):
        while True:
            time.sleep(10)
#由于UWSGI多进程模式直接复制进程空间,不能直接初始化ZOOKEEPER实例,防止回收重启时访问卡住
if SweetPySettings.RunMode == RunModeConst.UWSGIMode:
    import multiprocessing
    SweetPySettings.zookeeper_process = multiprocessing.Process(target=start_zookeeper, args=(SweetPySettings.CloudSettings,))
    SweetPySettings.zookeeper_process.daemon = False
    SweetPySettings.zookeeper_process.start()
    # zookeeper_on_line(SweetPySettings.CloudSettings)
else:
   import SweetPy.extend.django_runserver_plus
   SweetPy.extend.django_runserver_plus.Foo.online = zookeeper_on_line
   SweetPy.extend.django_runserver_plus.Foo.sweet_settings = SweetPySettings.CloudSettings


#######################################以下代码暂不需要#################################################
# def zookeeper_off_line():
#     global sweet_settings
#     if not sweet_settings:
#         return
#     _zk_info = sweet_settings['zk']['zkConnectionString']
#     _n_p = sweet_settings['zk']['zkDigestAuthString']
#     _zk_username = _n_p[:_n_p.find(':')]
#     _zk_password = _n_p[_n_p.find(':') + 1:]
#     zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)
#
#     app_name = settings.SWEET_CLOUD_APPNAME
#     app_host = get_local_ip()#settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST
#     app_port = settings.SWEET_CLOUD_APPPORT
#     app_version = settings.SWEET_CLOUD_VERSION
#
#     app_info_realms = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, '1.0',
#                                                     state='Stoped')  # Running  Stoped
#     zk_plus.set_realms(app_name, app_port, app_info_realms)
#     print('APP[' + app_name + ']已从应用云平台离线!')
#     filename = get_sweet_settings_local_filename()
#     if os.path.exists(filename):
#         with open(filename,'w') as f:
#             f.write(json.dumps({},ensure_ascii=False))
#
# def zookeeper_delete_self(sweet_settings):
#     _zk_info = sweet_settings['zk']['zkConnectionString']
#     _n_p = sweet_settings['zk']['zkDigestAuthString']
#     _zk_username = _n_p[:_n_p.find(':')]
#     _zk_password = _n_p[_n_p.find(':') + 1:]
#     zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)
#     app_name = settings.SWEET_CLOUD_APPNAME
#     app_port = settings.SWEET_CLOUD_APPPORT
#     zk_plus.delete_app_path(app_name,app_port)
#     print('APP[' + app_name + ']已从应用云平台删除!')
#
# import signal
#
# def stop(sig, former):
#     zookeeper_off_line()
#     quit(0)
# signal.signal(signal.SIGINT, stop)
# signal.signal(signal.SIGTERM, stop)
# sysstr = platform.system()
# if sysstr.lower() != 'windows':
#     signal.signal(signal.SIGHUP, stop)



# def add_data_watch(node_path,func):
#     result = False
#     global zk_plus
#     if zk_plus == None:
#         return result
#     zpw = ZookeeperPlusWatch(zk_plus)
#     if zpw.add_data_watch(node_path,func):
#         ZookeeperPlusWatch.watch_list.append(zpw)
#         result = True
#     return result
#
# def add_node_watch(node_path,func):
#     result = False
#     global zk_plus
#     if zk_plus == None:
#         return result
#     zpw = ZookeeperPlusWatch(zk_plus)
#     if zpw.add_node_watch(node_path, func):
#         ZookeeperPlusWatch.watch_list.append(zpw)
#         result = True
#     return result
# def p_8888(*args):
#     print('p_8888')
# def p_8889(*args):
#     print('p_8889')
# add_data_watch('/realms/python-sweet/8888',p_8888)
# add_data_watch('/realms/python-sweet/8889', p_8889)
# add_node_watch('/realms',p_8888)
# add_node_watch('/applications', p_8889)



#######################zookeeper数据结构#####################################
# {
#   "code": "success",
#   "data": {
#     "zk": {
#       "zkConnectionString": "10.86.87.180:2181",
#       "zkDigestAuthString": "sweetCloud:sweetCloud123"
#     },
#     "mqLogEnabled": true,
#     "mq": {
#       "connectionString": "10.86.87.118:5672",
#       "user": "sweet",
#       "password": "sweet123",
#       "traceLogQueueName": "request.trace.log",
#       "apmLogQueueName": "apm.log"
#     },
#     "gatewayUrl": "[disabled]",
#     "cloudSharedConfigurations": {
#       "sweet.framework.core.mvc.dynamic-resource.pattern": "/*",
#       "spring.datasource.validationQuery": "select '1' from dual",
#       "sweet.framework.redis.host": "10.86.87.179",
#       "management.contextPath": "/endpoints",
#       "sweet.event.redis.sentinel.master": "masterName",
#       "sweet.framework.session.redis.hosts.type": "sentinel",
#       "sweet.framework.session.redis.password": "",
#       "sweet.framework.session.parse-request.enabled": "true",
#       "spring.datasource.minIdle": "1",
#       "sweet.framework.rabbitmq.metrics.report.interval": "3000",
#       "sweet.framework.redis.hosts": "",
#       "sweet.framework.storage.fastdfs.connection-timeout": "5",
#       "spring.datasource.filters": "stat",
#       "sweet.framework.rabbitmq.userName": "guest",
#       "mybatis.typeAliasesPackage": "",
#       "spring.datasource.testOnReturn": "false",
#       "mybatis.mapperLocations": "classpath*:sql-mappers/**/*.xml,classpath*:sql-mappers-${spring.datasource.db-type:mysql}/**/*.xml",
#       "sweet.framework.core.mvc.error.handler.outputStackTrace": "false",
#       "spring.datasource.db-type": "mysql",
#       "spring.data.mongodb.repositories.enabled": "true",
#       "druid.stat.slowSqlMillis": "5000",
#       "spring.datasource.url": "jdbc:mysql://127.0.0.1:3306/test?useUnicode=true&characterEncoding=UTF-8",
#       "sweet.framework.core.mvc.error.handle.json": "true",
#       "sweet.cloud.service.client.native-service-first.policy": "enabled",
#       "sweet.event.redis.host": "10.86.87.179",
#       "server.context-path": "/",
#       "spring.datasource.driver-class-name": "com.mysql.jdbc.Driver",
#       "sweet.framework.core.i18n.resources.encoding": "utf-8",
#       "sweet.event.redis.password": "",
#       "sweet.framework.session.redis.namespace": "",
#       "sweet.framework.core.mvc.api.pattern": "/*",
#       "spring.freemarker.check-template-location": "false",
#       "sweet.framework.session.header-token.name": "sweet-token",
#       "sweet.framework.session.redis.pool.maxIdle": "8",
#       "sweet.cloud.apm.log.cron": "0/30 * * * * *",
#       "spring.freemarker.settings.template_update_delay": "0",
#       "spring.freemarker.settings.classic_compatible": "true",
#       "hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds": "10000",
#       "sweet.framework.storage.fastdfs.http.anti-steal-token": "false",
#       "sweet.framework.redis.sentinel.master": "masterName",
#       "sweet.framework.session.redis.database": "1",
#       "spring.freemarker.content-type": "text/html",
#       "spring.freemarker.settings.default_encoding": "UTF-8",
#       "spring.freemarker.expose-spring-macro-helpers": "true",
#       "sweet.cloud.apm.update.cron": "0/5 * * * * *",
#       "sweet.framework.socket.server.udp.server-name": "Sweet-UDP-Server",
#       "sweet.framework.rabbitmq.serialize.type": "1",
#       "sweet.framework.socket.server.tcp.enabled": "false",
#       "sweet.framework.socket.server.udp.port": "9999",
#       "sweet.event.redis.pool.maxWait": "-1",
#       "sweet.framework.core.http.request.trace": "true",
#       "sweet.framework.core.rest.invocation.connectTimeout": "3000",
#       "sweet.framework.redis.keys.normalize": "true",
#       "spring.freemarker.allow-session-override": "false",
#       "sweet.framework.core.rest.invocation.warning.limit": "2000",
#       "sweet.framework.socket.server.udp.session.timeout.check-interval": "60",
#       "spring.datasource.minEvictableIdleTimeMillis": "30000",
#       "sweet.framework.socket.server.udp.session.timeout": "120",
#       "springfox.documentation.swagger.v2.path": "/v2/api-docs",
#       "sweet.event.redis.database": "2",
#       "sweet.framework.core.mybatis.page-helper.offsetAsPageNum": "true",
#       "spring.datasource.password": "",
#       "sweet.framework.core.mybatis.mapper.scan.annotation": "org.apache.ibatis.annotations.Mapper",
#       "sweet.framework.redis.timeout": "2000",
#       "sweet.event.redis.pool.maxActive": "50",
#       "sweet.framework.rabbitmq.port": "5672",
#       "spring.datasource.maxActive": "5",
#       "spring.freemarker.expose-session-attributes": "true",
#       "server.session.timeout": "1800",
#       "logging.level.root": "INFO",
#       "sweet.event.redis.pool.minIdle": "0",
#       "sweet.framework.session.redis.port": "6379",
#       "sweet.framework.core.mvc.api.i18n.basename": "classpath*:i18n/api",
#       "spring.output.ansi.enabled": "ALWAYS",
#       "mybatis.typeHandlersPackage": "",
#       "sweet.framework.socket.server.udp.enabled": "false",
#       "sweet.framework.storage.type": "fastdfs",
#       "sweet.framework.redis.pool.maxActive": "50",
#       "sweet.framework.core.i18n.locale.param": "lang",
#       "sweet.framework.redis.pool.maxWait": "-1",
#       "sweet.framework.core.mvc.upload.maxFileSize": "10MB",
#       "spring.datasource.testOnBorrow": "false",
#       "sweet.framework.core.http.restful.doc.swagger.licenseUrl": "http://www.apache.org/licenses/LICENSE-2.0",
#       "hystrix.threadpool.default.coreSize": "20",
#       "sweet.framework.core.i18n.enabled": "true",
#       "sweet.framework.core.http.restful.doc.swagger.title": "${spring.application.name:sweet-application} Restful API Documentation",
#       "sweet.framework.storage.fastdfs.network-timeout": "30",
#       "sweet.event.redis.pool.maxIdle": "8",
#       "spring.profiles.active": " configuration,dev",
#       "sweet.framework.redis.namespace": "",
#       "sweet.event.redis.hosts.type": "sentinel",
#       "sweet.framework.socket.server.tcp.server-name": "Sweet-TCP-Server",
#       "sweet.framework.core.http.defence.csrf": "false",
#       "spring.freemarker.order": "1",
#       "spring.freemarker.cache": "false",
#       "sweet.framework.redis.hosts.type": "sentinel",
#       "sweet.framework.core.http.restful.doc.swagger.termsOfServiceUrl": "http://swagger.io/terms/",
#       "sweet.framework.rabbitmq.host": "10.86.86.13",
#       "logging.pattern.file": "%d{yyyy-MM-dd HH:mm:ss.SSS} ${LOG_LEVEL_PATTERN:-%5p} ${PID:- } %appId %rid --- [%t] %-40.40logger{39} : %m%n${LOG_EXCEPTION_CONVERSION_WORD:%wEx}",
#       "sweet.framework.core.mybatis.page-helper.rowBoundsWithCount": "true",
#       "sweet.framework.session.redis.pool.maxActive": "50",
#       "sweet.framework.storage.fastdfs.tracker-domain": "http://www.igap.cc/",
#       "logging.file": "${user.home:./}/sweet-logs/${spring.application.name:sweet-application}-${spring.application.index:${server.port:8080}}.log",
#       "hystrix.threadpool.default.queueSizeRejectionThreshold": "-1",
#       "sweet.framework.rabbitmq.addresses": "",
#       "sweet.event.redis.namespace": "",
#       "sweet.framework.session.redis.host": "10.86.87.179",
#       "sweet.framework.redis.pool.minIdle": "0",
#       "sweet.framework.session.redis.hosts": "",
#       "sweet.event.redis.consumer.thread-pool-size": "10",
#       "sweet.framework.redis.monitor.output.interval": "300",
#       "spring.datasource.testWhileIdle": "true",
#       "logging.level.cn.evun.sweet.common.tracer.ThreadLocalProcessTracer": "INFO",
#       "sweet.framework.core.http.restful.doc.api.groups": " ",
#       "sweet.framework.storage.fastdfs.tracker-servers": "10.86.87.208:22122,10.86.87.208:22122,10.86.87.208:22122",
#       "sweet.framework.rabbitmq.vhost": "/",
#       "spring.freemarker.enabled": "true",
#       "sweet.framework.core.mvc.error.handle": "true",
#       "sweet.framework.rabbitmq.password": "guest",
#       "spring.data.mongodb.uri": "mongodb://127.0.0.1:27017/test",
#       "sweet.framework.socket.server.tcp.session.timeout.check-interval": "600",
#       "hystrix.threadpool.default.maxQueueSize": "-1",
#       "sweet.cloud.service.client.packages": "",
#       "sweet.framework.redis.password": "",
#       "spring.freemarker.request-context-attribute": "",
#       "server.address": "0.0.0.0",
#       "sweet.framework.core.http.restful.doc.swagger.license": "Apache 2.0",
#       "sweet.framework.core.freemarker.auto-escape-enabled": "false",
#       "sweet.event.redis.log.queue.mame": "sweet:event:bus:log:queue",
#       "sweet.framework.redis.pool.maxIdle": "8",
#       "spring.datasource.maxOpenPreparedStatements": "-1",
#       "sweet.framework.core.i18n.defaultLocale": "zh_CN",
#       "spring.datasource.username": "root",
#       "sweet.framework.session.sso.enabled": "true",
#       "sweet.framework.core.rest.invocation.readTimeout": "-1",
#       "sweet.framework.core.http.defence.xss": "true",
#       "sweet.framework.storage.fastdfs.http.secret-key": "FastDFS1234567890",
#       "sweet.event.redis.hosts": "",
#       "sweet.framework.core.http.restful.doc.modelPackages": "",
#       "spring.datasource.timeBetweenEvictionRunsMillis": "10000",
#       "sweet.framework.socket.server.tcp.session.timeout": "120",
#       "sweet.framework.core.mvc.upload.storageLocation": "",
#       "hystrix.command.default.fallback.enabled": "false",
#       "spring.datasource.type": "com.alibaba.druid.pool.DruidDataSource",
#       "sweet.framework.rabbitmq.autoListen": "true",
#       "spring.datasource.initialSize": "2",
#       "logging.pattern.console": "%clr(%d{yyyy-MM-dd HH:mm:ss.SSS}){faint} %clr(${LOG_LEVEL_PATTERN:-%5p}) %clr(${PID:- }){magenta} %appId %rid %clr(---){faint} %clr([%15.15t]){faint} %clr(%-40.40logger{39}){cyan} %clr(:){faint} %m%n${LOG_EXCEPTION_CONVERSION_WORD:%wEx}",
#       "sweet.framework.storage.fastdfs.charset": "UTF-8",
#       "sweet.framework.auth.path-matching.performance.log": "true",
#       "sweet.framework.core.mvc.api.i18n.locale": "zh_CN",
#       "sweet.framework.core.mybatis.mapper.scan.basePackages": "",
#       "sweet.cloud.routing.map": " ",
#       "sweet.framework.redis.database": "0",
#       "sweet.framework.core.i18n.resources.baseName": "i18n/messages",
#       "sweet.framework.session.request-param.name": "__ticket__",
#       "management.address": "0.0.0.0",
#       "sweet.framework.session.redis.sentinel.master": "masterName",
#       "spring.freemarker.allow-request-override": "false",
#       "sweet.framework.redis.port": "6379",
#       "mybatis.configuration.auto-mapping-behavior": "FULL",
#       "hystrix.command.default.circuitBreaker.enabled": "true",
#       "sweet.framework.core.mvc.data-binder.date.useGMTTimeZone": "false",
#       "sweet.framework.session.parse-header.enabled": "true",
#       "sweet.framework.redis.keys.namespace": "",
#       "management.port": "-1",
#       "sweet.framework.core.mybatis.page-helper.reasonable": "true",
#       "server.tomcat.max-threads": "300",
#       "sweet.framework.core.http.restful.doc": "true",
#       "spring.datasource.name": "21",
#       "server.port": "${spring.application.index}",
#       "sweet.framework.auth.mode": "MIXED",
#       "spring.freemarker.charset": "UTF-8",
#       "sweet.framework.core.http.restful.doc.swagger.description": "",
#       "spring.freemarker.suffix": ".ftl",
#       "spring.datasource.poolPreparedStatements": "false",
#       "spring.datasource.maxWait": "-1",
#       "sweet.event.redis.topic.mame": "sweet:event:bus:topic",
#       "sweet.framework.session.redis.pool.maxWait": "-1",
#       "spring.freemarker.template-loader-path": "classpath*:templates/",
#       "sweet.event.redis.port": "6379",
#       "sweet.framework.storage.fastdfs.http.port": "80",
#       "sweet.framework.socket.server.tcp.port": "9999",
#       "spring.freemarker.expose-request-attributes": "false",
#       "spring.freemarker.prefer-file-system-access": "false",
#       "sweet.framework.core.mvc.upload.maxRequestSize": "100MB",
#       "sweet.event.redis.timeout": "2000",
#       "sweet.framework.core.http.restful.doc.swagger.contract": "sweet-group@geely.com",
#       "spring.mvc.throw-exception-if-no-handler-found": "true",
#       "sweet.framework.session.redis.pool.minIdle": "0",
#       "sweet.framework.session.cross-context.enabled": "true"
#     },
#     "applicationInstanceConfigurations": {
#       "spring.datasource.db-type": "",
#       "spring.datasource.username": "postgres",
#       "spring.datasource.password": "postgres",
#       "sweet.framework.socket.server.tcp.port": "9999",
#       "spring.datasource.url": "127.0.0.1:5432",
#       "spring.datasource.name": "sdlc",
#       "spring.datasource.maxActive": "5",
#       "spring.datasource.minIdle": "1"
#     },
#     "attributes": {}
#   },
#   "message": "API调用成功"
# }
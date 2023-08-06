from .configurations import SweetPySettings
from django.conf import settings

print('检查是否注册跟踪组件...')

#是否安装访问记录中件间
if hasattr(settings, 'SWEET_ACCESS_LOG_FILE_PATH') and (settings.SWEET_ACCESS_LOG_FILE_PATH):
    SweetPySettings.IsWriteTrackerLogLocal = True

if hasattr(settings, 'SWEET_RABBITMQ_ENABLED') and (settings.SWEET_RABBITMQ_ENABLED):
    SweetPySettings.IsSendTrackerToRabbitMQ = True


if SweetPySettings.IsSendTrackerToRabbitMQ or SweetPySettings.IsWriteTrackerLogLocal:
    settings.MIDDLEWARE.insert(0,'SweetPy.django_middleware.tracker.request_tracker')

    #数据时间
    from rest_framework import mixins
    import SweetPy.extend.mixins_plus
    mixins.ListModelMixin = SweetPy.extend.mixins_plus.ListModelMixin
    mixins.RetrieveModelMixin = SweetPy.extend.mixins_plus.RetrieveModelMixin
    mixins.DestroyModelMixin = SweetPy.extend.mixins_plus.DestroyModelMixin
    mixins.CreateModelMixin = SweetPy.extend.mixins_plus.CreateModelMixin

    #视图时间
    import SweetPy.extend.api_view_plus

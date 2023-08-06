
import SweetPy.init_program
import SweetPy.set_settingfile
from .configurations import SweetPySettings
from .const import *

if SweetPySettings.RunMode != RunModeConst.UWSGIMode:
    import SweetPy.set_http_port

if SweetPySettings.RunMode == RunModeConst.PythonModeParent:
    pass
elif (SweetPySettings.RunMode == RunModeConst.UWSGIMode) or (SweetPySettings.RunMode == RunModeConst.PythonModeChinldren):
    import SweetPy.install_apps
    import SweetPy.add_tracker
    import SweetPy.add_response_header
    import SweetPy.add_handler
    import SweetPy.extend.swagger_plus
    import SweetPy.add_cloud
    if SweetPySettings.IsCloudConnected:
        import SweetPy.add_cloud_db_option
        import SweetPy.add_zookeeper
        import SweetPy.add_sso
        import SweetPy.setting
    import SweetPy.sweet_framework.sweet_framework_views
    import SweetPy.sweet_framework_cloud.sweet_framework_cloud_views
    import SweetPy.geely_auth.geely_sso
    import SweetPy.scheduler
elif SweetPySettings.RunMode == RunModeConst.PythonModeTest:
    import SweetPy.install_apps
    from django.conf import settings
    settings.SWEET_CLOUD_ENABLED = False
    import SweetPy.add_response_header
    import SweetPy.add_handler
    import SweetPy.extend.swagger_plus
else:
    import SweetPy.install_apps
    import SweetPy.extend.swagger_plus

from .configurations import SweetPySettings

InstancePrams = None
if SweetPySettings.CloudSettings:
    InstancePrams = SweetPySettings.CloudSettings.get('applicationInstanceConfigurations',None)
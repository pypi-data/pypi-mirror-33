#
from django.conf import settings

def set_http_port():
    from django.core.management.commands.runserver import Command
    if hasattr(settings,'SWEET_CLOUD_APPPORT') and settings.SWEET_CLOUD_APPPORT:
        Command.default_port = settings.SWEET_CLOUD_APPPORT
set_http_port()
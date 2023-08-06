#
from django.conf import settings

def set_http_port():
    from django.core.management.commands.runserver import Command
    Command.default_port = settings.SWEET_CLOUD_APPPORT
set_http_port()
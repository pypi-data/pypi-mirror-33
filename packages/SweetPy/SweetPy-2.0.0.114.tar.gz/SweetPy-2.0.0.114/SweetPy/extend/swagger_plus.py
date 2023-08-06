print('注册Swagger组件...')

from sys import argv

from django.conf.urls import url, RegexURLResolver, RegexURLPattern
# from rest_framework_swagger.views import get_swagger_view
from .swagger_view import get_swagger_view
from django import conf
from django.conf import settings
from django.core.checks.urls import check_resolver
from django.core.checks.registry import register, Tags
import django.core.checks.urls

from django.utils.functional import cached_property
from django.urls.resolvers import LocaleRegexProvider
from django.core.exceptions import ImproperlyConfigured

if hasattr(settings,'SWEET_CLOUD_APPNAME') and settings.SWEET_CLOUD_APPNAME:
    schema_view = get_swagger_view(title=settings.SWEET_CLOUD_APPNAME + ' Restful API Documentation')
else:
    schema_view = get_swagger_view('Project Restful API Documentation')
conf.settings.INSTALLED_APPS.append('rest_framework_swagger')
swagger_regex = RegexURLPattern('^swagger-ui.html$', schema_view)
if not('uwsgi' in argv):
    @register(Tags.urls)
    def check_url_config(app_configs, **kwargs):
        if getattr(settings, 'ROOT_URLCONF', None):
            from django.urls import get_resolver
            resolver = get_resolver()
            global swagger_regex
            resolver.url_patterns.append(swagger_regex)
            return check_resolver(resolver)
        return []
    django.core.checks.urls.check_url_config = check_url_config
else:
    class RegexURLResolver_plus(LocaleRegexProvider):
        @cached_property
        def url_patterns(self):
            # urlconf_module might be a valid set of patterns, so we default to it
            patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
            try:
                iter(patterns)
            except TypeError:
                msg = (
                    "The included URLconf '{name}' does not appear to have any "
                    "patterns in it. If you see valid patterns in the file then "
                    "the issue is probably caused by a circular import."
                )
                raise ImproperlyConfigured(msg.format(name=self.urlconf_name))
            patterns.append(swagger_regex)
            return patterns
    from django.urls.resolvers import RegexURLResolver
    RegexURLResolver.url_patterns = RegexURLResolver_plus.url_patterns

import coreapi
from coreapi.compat import force_bytes
from openapi_codec import OpenAPICodec as _OpenAPICodec
from openapi_codec.encode import generate_swagger_object
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework import status
import simplejson as json
from rest_framework_swagger.settings import swagger_settings
from ..func_plus import FuncHelper
import platform
import os
class OpenAPICodec(_OpenAPICodec):
    def encode(self, document, extra=None, **options):
        if hasattr(settings, 'SWEET_SWAGGER_JSON_FILE') and (settings.SWEET_SWAGGER_JSON_FILE):
            if platform.system().lower() == 'windows':
                path = os.getcwd() + settings.SWEET_SWAGGER_JSON_FILE
                path = path.replace('/','\\')
            else:
                path = os.getcwd() + settings.SWEET_SWAGGER_JSON_FILE
                path = path.replace('\\', '/')
            if FuncHelper.check_file_exists(path):
                with open(path, 'r', encoding='utf8') as f:
                    json_str = f.read()
                    return force_bytes(json_str)
            else:
                raise Exception('SwaggerJsonFile ' + settings.SWEET_SWAGGER_JSON_FILE + ' Not Found!')
        else:
            # if not isinstance(document, coreapi.Document):
            #     raise TypeError('Expected a `coreapi.Document` instance')
            #
            # data = generate_swagger_object(document)
            # if isinstance(extra, dict):
            #     data.update(extra)
            #
            # return force_bytes(json.dumps(data))
            return document

class OpenAPIRenderer(BaseRenderer):
    media_type = 'application/openapi+json'
    charset = None
    format = 'openapi'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context['response'].status_code != status.HTTP_200_OK:
            return JSONRenderer().render(data)
        extra = self.get_customizations()
        if platform.system().lower() == 'windows':
            return OpenAPICodec().encode(data['data'], extra=extra)
        else:
            return OpenAPICodec().encode(data, extra=extra)

    def get_customizations(self):
        """
        Adds settings, overrides, etc. to the specification.
        """
        data = {}
        if swagger_settings.SECURITY_DEFINITIONS:
            data['securityDefinitions'] = swagger_settings.SECURITY_DEFINITIONS

        return data

import rest_framework_swagger.renderers
rest_framework_swagger.renderers.OpenAPIRenderer.render = OpenAPIRenderer.render


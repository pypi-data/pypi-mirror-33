import os
import json
from collections import OrderedDict

from openapi_codec import OpenAPICodec
from openapi_codec.encode import generate_swagger_object
from coreapi.compat import force_bytes

from django.conf import settings

from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView

import rest_framework_swagger.renderers as renderers

from coreapi.document import Document
def _parse_document(data, base_url=None):
    schema_url = base_url
    base_url = _get_document_base_url(data, base_url)
    info = _get_dict(data, 'info')
    title = _get_string(info, 'title')
    description = _get_string(info, 'description')
    consumes = get_strings(_get_list(data, 'consumes'))
    paths = _get_dict(data, 'paths')
    content = {}
    for path in paths.keys():
        url = base_url + path.lstrip('/')
        spec = _get_dict(paths, path)
        default_parameters = get_dicts(_get_list(spec, 'parameters'))
        for action in spec.keys():
            action = action.lower()
            if action not in ('get', 'put', 'post', 'delete', 'options', 'head', 'patch'):
                continue
            operation = _get_dict(spec, action)

            # Determine any fields on the link.
            has_body = False
            has_form = False

            fields = []
            parameters = get_dicts(_get_list(operation, 'parameters', default_parameters), dereference_using=data)
            for parameter in parameters:
                name = _get_string(parameter, 'name')
                location = _get_string(parameter, 'in')
                required = _get_bool(parameter, 'required', default=(location == 'path'))
                if location == 'body':
                    has_body = True
                    schema = _get_dict(parameter, 'schema', dereference_using=data)
                    expanded = _expand_schema(schema)
                    if expanded is not None:
                        # TODO: field schemas.
                        expanded_fields = [
                            Field(
                                name=field_name,
                                location='form',
                                required=is_required,
                                schema=coreschema.String(description=field_description)
                            )
                            for field_name, is_required, field_description in expanded
                            if not any([field.name == field_name for field in fields])
                        ]
                        fields += expanded_fields
                    else:
                        # TODO: field schemas.
                        field_description = _get_string(parameter, 'description')
                        field = Field(
                            name=name,
                            location='body',
                            required=required,
                            schema=coreschema.String(description=field_description)
                        )
                        fields.append(field)
                else:
                    if location == 'formData':
                        has_form = True
                        location = 'form'
                    field_description = _get_string(parameter, 'description')
                    # TODO: field schemas.
                    field = Field(
                        name=name,
                        location=location,
                        required=required,
                        schema=coreschema.String(description=field_description)
                    )
                    fields.append(field)

            link_consumes = get_strings(_get_list(operation, 'consumes', consumes))
            encoding = ''
            if has_body:
                encoding = _select_encoding(link_consumes)
            elif has_form:
                encoding = _select_encoding(link_consumes, form=True)

            link_title = _get_string(operation, 'summary')
            link_description = _get_string(operation, 'description')
            link = Link(url=url, action=action, encoding=encoding, fields=fields, title=link_title, description=link_description)

            # Add the link to the document content.
            tags = get_strings(_get_list(operation, 'tags'))
            operation_id = _get_string(operation, 'operationId')
            if tags:
                tag = tags[0]
                prefix = tag + '_'
                if operation_id.startswith(prefix):
                    operation_id = operation_id[len(prefix):]
                if tag not in content:
                    content[tag] = {}
                content[tag][operation_id] = link
            else:
                content[operation_id] = link

    return Document(
        url=schema_url,
        title=title,
        description=description,
        content=content,
        media_type='application/openapi+json'
    )


def get_swagger_view(title=None, url=None, patterns=None, urlconf=None):
    """
    Returns schema view which renders Swagger/OpenAPI.
    """
    class SwaggerSchemaView(APIView):
        _ignore_model_permissions = True
        exclude_from_schema = True
        permission_classes = [AllowAny]
        renderer_classes = [
            CoreJSONRenderer,
            renderers.OpenAPIRenderer,
            renderers.SwaggerUIRenderer
        ]

        def load_swagger_json(self, doc):
            """
            加载自定义swagger.json文档
            """
            if not (hasattr(settings, 'SWEET_SWAGGER_JSON_FILE_EXTEND') and (settings.SWEET_SWAGGER_JSON_FILE_EXTEND)):
                return None
            if not os.path.exists(os.getcwd() + settings.SWEET_SWAGGER_JSON_FILE_EXTEND):
                return None

            data = generate_swagger_object(doc)
            with open(os.getcwd() + settings.SWEET_SWAGGER_JSON_FILE_EXTEND, 'r', encoding='utf-8') as s:
                doc_json = json.load(s, object_pairs_hook=OrderedDict)

            data['paths'].update(doc_json.pop('paths'))
            data.update(doc_json)

            jsondata = json.dumps(data)
            forcedata = force_bytes(jsondata)
            # decdata = OpenAPICodec().decode(forcedata,base_url=data.get('basePath',''))
            #
            #
            # _parse_document(data.get('basePath',''),)
            # doc = Document(url=data.get('basePath',''), title=data.get('info').get('basePath',''), description=data.get('info').get('description',''), media_type=None, content=data)
            return forcedata

        def get(self, request):
            generator = SchemaGenerator(
                title=title,
                url=url,
                patterns=patterns,
                urlconf=urlconf
            )
            schema = generator.get_schema(request=request)

            if not schema:
                raise exceptions.ValidationError(
                    'The schema generator did not return a schema Document'
                )
            document = self.load_swagger_json(schema)
            if document:
                result = Response(document)
                return result
            else:
                return Response(schema)

    return SwaggerSchemaView.as_view()

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import resolve
from django.utils.six.moves.urllib import parse as urlparse

from rest_framework.compat import coreapi
from rest_framework.schemas import AutoSchema


class OrcSchema(AutoSchema):
    """
    Schema View creation based on HTTP Method
    """
    def __init__(self, *args, **kwargs):
        super(OrcSchema, self).__init__(manual_fields=kwargs.get('manual_fields', []))
        self.methods_fields = {k: v for k, v in kwargs.items() if k != 'manual_fields'}
        self.all_fields = kwargs.get('fields', [])

        for _, fields in self.methods_fields.items():
            self.all_fields.extend(field for field in fields if field not in self.all_fields)

    def get_link(self, path, method, base_url):
        fields = [
            *self.get_path_fields(path, method),
            *self.get_serializer_fields(path, method),
            *self.get_pagination_fields(path, method),
            *self.get_filter_fields(path, method)
        ]

        manual_fields = self.get_manual_fields(path, method)
        fields = self.update_fields(fields, manual_fields)

        http_method_fields = self.methods_fields.get(f"{method.lower()}_fields", [])
        fields = self.update_fields(fields, http_method_fields)

        try:
            url_name = resolve(path).url_name
            if url_name is not None:
                url_name = '_'.join(url_name.split('-')[1:]).lower()
                view_method_fields = tuple(self.methods_fields.get(f"{url_name}_fields", []))
                fields = self.update_fields(fields, view_method_fields)
        except Exception as e:
            # print(f"URL Error: {e}")
            pass

        path = path[1:] if base_url and path.startswith('/') else path
        encoding = self.get_encoding(path, method) if fields and any(f.location in ('form', 'body') for f in fields) else None

        return coreapi.Link(
            url=urlparse.urljoin(base_url, path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=self.get_description(path, method)
        )

    @property
    def query_fields(self):
        return [field for field in self.all_fields if field.location == 'query']

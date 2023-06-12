from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector, SwaggerAutoSchema
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination


class RestResponsePagination(PaginatorInspector):
    """
    Provides response schema pagination

    Warpping for django-rest-framework's LimitOffsetPagination, PageNumberPagination and ElasticPageNumberPagination
    """

    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        # if isinstance(paginator, (LimitOffsetPagination, PageNumberPagination, ElasticPageNumberPagination)):
        #     paged_schema = openapi.Schema(
        #         type=openapi.TYPE_OBJECT,
        #         properties=OrderedDict((
        #             ('pagination', openapi.Schema(
        #                 type=openapi.TYPE_OBJECT,
        #                 properties={
        #                     'current': openapi.Schema(type=openapi.TYPE_INTEGER),
        #                     'total': openapi.Schema(type=openapi.TYPE_INTEGER),
        #                     'totalPages': openapi.Schema(type=openapi.TYPE_INTEGER),
        #                     'pageSize': openapi.Schema(type=openapi.TYPE_INTEGER),
        #                 },
        #                 required=['current', 'total'])),
        #             ('list', response_schema),
        #         )),
        #         required=['list']
        #     )

        return paged_schema


class EsAutoSchema(SwaggerAutoSchema):
    """
    Elasticsearch inspector for APIView

    Responsible for per-view instrospection and schema generation.
    """

    def get_es_filter_fields(self):
        fields = []
        for filter_backend in self.view.es_filter_backends:
            fields += filter_backend().get_schema_fields(self.view)
        return fields

    def get_filter_parameters(self):
        fields = super(EsAutoSchema, self).get_filter_parameters()
        # fields += self.get_es_filter_fields()
        # print(fields)
        return fields

    def get_es_pagination_fields(self):
        if not self.is_list_view():
            return []

        pagination = getattr(self.view, 'es_pagination_class', None)
        print('pagination', pagination)
        print('view', self.view)
        if not pagination:
            return []

        return pagination().get_schema_fields(self.view)

    def get_pagination_parameters(self):
        fields = super(EsAutoSchema, self).get_pagination_parameters()
        fields += self.get_es_pagination_fields()
        return fields

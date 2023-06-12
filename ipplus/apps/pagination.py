from collections import OrderedDict

import six
from django.core.paginator import InvalidPage
# from django.utils import six
from rest_framework import pagination
from rest_framework.exceptions import NotFound
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_description = '分页查询的页码'
    page_size_query_description = '每页返回结果的数量，默认 10'

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None
        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)

        # limit = int(paginator.num_pages * 0.3)
        # limit = 10
        # # 如果是 DomainList 接口 并且 是认证通过的用户 并且 是试用用户，超过 10页 内容提示异常
        # if (view.__class__.__name__ == 'DomainViewSet'
        #     and request.user.is_authenticated
        #     and request.user.is_trial
        #     and int(page_number) > limit):
        #     raise TrialDenied()

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pagination', {
                'current': self.page.number,
                'total': self.page.paginator.count,
                'totalPages': self.page.paginator.num_pages,
                'pageSize': self.get_page_size(self.request),
                # 'next': self.get_next_link(),
                # 'previous': self.get_previous_link(),
            }),
            ('list', data)
        ]))

# class ElasticPageNumberPagination(pagination.PageNumberPagination):
#     """
#     Elasticsearch 分页器（未用aggregations去重）
#     """
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_count = 10000
#     facets = None
#     page_query_description = '分页查询的页码'
#     page_size_query_description = '每页返回结果的数量，默认 10'
#
#     def _get_count(self, search):
#         response = search[0:0].execute()
#         return response.hits.total
#
#     def paginate_search(self, search, request, view=None):
#         """
#         Paginate a queryset if required, either returning a
#         page object, or `None` if pagination is not configured for this view.
#         """
#         self.page_size = self.get_page_size(request)
#         if not self.page_size:
#             return None
#
#         self.limit = self.page_size
#         if self.limit is None:
#             return None
#
#         self.page_number = int(
#             request.query_params.get(self.page_query_param, 1))
#         if self.page_number <= 0:
#             self.page_number = 1
#
#         if self.page_number * self.page_size > self.max_count:
#             raise NotFound()
#
#         self.count = self._get_count(search)
#         # if self.count > self.max_count:
#         #     self.count = self.max_count
#
#         self.offset = (self.page_number - 1) * self.page_size
#         hits = max(1, self.count)
#         self.total_pages = int(ceil(hits / float(self.page_size)))
#
#         self.request = request
#         if self.count > self.limit and self.template is not None:
#             self.display_page_controls = True
#
#         if self.count == 0 or self.offset > self.count:
#             return []
#         resp = search[self.offset:self.offset + self.limit].execute()
#         self.facets = getattr(resp, 'aggregations', None)
#         return resp
#
#     def get_facets(self, facets=None):
#         """Get facets.
#
#         :param facets:
#         :return:
#         """
#         if facets is None:
#             facets = self.facets
#
#         if not facets:
#             return None
#
#         if hasattr(facets, '_d_'):
#             stat = facets._d_.get('stat')
#             if stat and stat.get('buckets'):
#                 for item in stat.get('buckets'):
#                     spider_name = item.pop('key')
#                     item['spider_name'] = spider_name
#                     item['key'] = SPIDER_MAP.get(spider_name)
#             return facets._d_
#
#     def get_paginated_response(self, data):
#         data = [
#             ('pagination', {
#                 'current': self.page_number,
#                 'total': self.count,
#                 'totalPages': self.total_pages,
#                 'pageSize': self.page_size,
#             }),
#             ('list', data),
#         ]
#         facets = self.get_facets()
#         if facets is not None:
#             data.append(
#                 ('facets', facets),
#             )
#
#         return Response(OrderedDict(data))


# class ElasticCardinalityPagination(ElasticPageNumberPagination):
#     """
#     Elasticsearch 分页器（用aggregations去重）
#     search.aggs.bucket('count', 'cardinality', field='title')
#     """
#     cardinality_field = 'title'
#
#     def _get_count(self, search):
#         search.aggs.bucket('count', 'cardinality', field=self.cardinality_field)
#         response = search[0:0].execute()
#         return response.aggregations.count.value


# class UniqueRawTitlePagination(ElasticCardinalityPagination):
#     """
#     Elasticsearch 分页器（用aggregations去重）
#     search.aggs.bucket('count', 'cardinality', field='title')
#     """
#     cardinality_field = 'title.raw'

import logging
import re
from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from django.utils.encoding import escape_uri_path
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from config.constants import AWDB_FILE_PATH
from ipplus.utils.aiwen_lib import awdb
from ipplus.utils.net import lazy_asn

logger = logging.getLogger(__name__)


class QueryIPV4APIView(APIView):
    """
    IPV4查询接口

    tttt
    """

    @swagger_auto_schema(
        required=['ipv4', ],
        manual_parameters=[
            openapi.Parameter('ipv4', in_=openapi.IN_QUERY, description='ipv4文本内容(以逗号分隔)', type=openapi.TYPE_STRING),
    ])
    def get(self, request):
        data = request.query_params.get("ipv4")
        if not data:
            return Response({"operation": "failed",
                             "detail": 'ipv4参数不能为空，正确格式：10.10.10.10,11.11.11.11,22.22.22.22'},
                             status=HTTP_400_BAD_REQUEST)
        else:
            data = data.replace(" ", "").replace("\n", "").replace("\t", "")
            ipv4_list = data.split(",")
            #
            output = self.handle(ipv4_list)
            # 设置HttpResponse的类型
            file_name = escape_uri_path("ipplus_info.xlsx")
            http_response = HttpResponse(content_type="application/vnd.ms-excel")
            http_response.content = output.getvalue()
            http_response["Content-Disposition"] = f"attachment; filename={file_name}"
            return http_response

    @swagger_auto_schema(request_body=openapi.Schema(
        # manual_parameters=[
        #     openapi.Parameter('meta_id', in_=openapi.IN_PATH, description='列表页返回的ID', type=openapi.TYPE_STRING),
        # ],
        type=openapi.TYPE_OBJECT,
        required=['ipv4', ],
        properties={
            'ipv4': openapi.Schema(
                type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING), description='ipv4列表'
            ),
        }
    ))
    def post(self, request):
        data = request.data
        ipv4_list = data.get('ipv4')
        if not ipv4_list:
            return Response({"operation": "failed",
                             "detail": 'ipv4参数不能为空'},
                            status=HTTP_400_BAD_REQUEST)
        if not isinstance(ipv4_list, list):
            return Response({"operation": "failed",
                             "detail": '参数类型有误，正确格式: ["10.10.10.10", "11.11.11.11", "22.22.22.22"]'},
                            status=HTTP_400_BAD_REQUEST)
        #
        output = self.handle(data)
        # 设置HttpResponse的类型
        file_name = escape_uri_path("ipplus_info.xlsx")
        http_response = HttpResponse(content_type="application/vnd.ms-excel")
        http_response.content = output.getvalue()
        http_response["Content-Disposition"] = f"attachment; filename={file_name}"
        return http_response

    def check_ipv4(self, ipv4):
        compile_ip = re.compile(
            '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
        if compile_ip.match(ipv4):
            return True
        else:
            return False

    def handle(self, data):
        """处理方法"""

        reader = awdb.open_database(AWDB_FILE_PATH)
        data_list = []
        for ipv4 in data:
            status = self.check_ipv4(ipv4)
            if status is False:
                data_dict = {
                    "ip": ipv4,
                    "remark": "非ipv4地址"
                }
            else:
                # 使用诶文ipip库
                try:
                    record, prefix_len = reader.get_with_prefix_len(ipv4)
                except Exception as e:
                    logger.error(f"get_with_prefix_len, {e}")
                    record = {}
                # 使用ipip 库
                data_dict = {
                    "ip": ipv4,
                    "continent": record.get("continent", b"").decode(),
                    "areacode": record.get("areacode", b"").decode(),
                    "country": record.get("country", b"").decode(),
                    "zipcode": record.get("zipcode", b"").decode(),
                    "timezone": record.get("timezone", b"").decode(),
                    "accuracy": record.get("accuracy", b"").decode(),
                    "scene": record.get("scene", b"").decode(),
                    "asnumber": record.get("asnumber", b"").decode(),
                    "isp": record.get("isp", b"").decode(),
                    "owner": record.get("owner", b"").decode(),
                    "multiAreas": {key: value.decode() for item in record.get("multiAreas", []) for key, value in
                                   item.items()},
                    "user_type": record.get("user_type", b"").decode(),
                    "user": record.get("user", b"").decode(),
                    "correctness": record.get("correctness", b"").decode(),
                    "lazy_asn": lazy_asn.lookup(ipv4),
                }
            # if info.country.lower().__contains__("china"):
            data_list.append(data_dict)

        #
        df_data = pd.DataFrame(data_list)
        # 准备写入到IO中
        output = BytesIO()
        writer = pd.ExcelWriter(output)
        df_data.to_excel(writer)
        #
        output.seek(0)
        writer.save()
        return output

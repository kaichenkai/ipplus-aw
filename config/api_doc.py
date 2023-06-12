from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions

doc_desc = """
# 1.概述
本文档描述了查询IPV4 isp、asn、geo信息相关的接口。系统中所有的接口均以RESTful API的形式定义，便于接口统一和管理后台调用。

## 1.1.请求参数
请求的参数包含必须参数和可选参数两种类型
在 POST 请求方法中，相关参数必须为 json 编码后放置请求体中进行请求。

## 1.2.分页查询格式
查询结果大于10条的查询类接口须提供分页查询功能，分页查询接口除了各接口自定义传入参数外，
可以传入非必须参数page（页码）、page_size（页面大小,最大值100），返回结果如下所示：
```bash
{
    "pagination": {
        "current": 1, // 当前页
        "total": 1,  //总条数
        "totalPages": 1, // 总页数
        "pageSize": 10 // 页大小
    },
    "list": [] // 分页内容
}
```

## 1.3.响应结果字段说明
| 字段名      | 子属性(字段类型)  | 字段说明                  |
| ----------- | ----------------- | ------------------------- |
| continent   | String            | 大洲，包含七大洲和保留 IP |
| areacode    | String            | 国家编码                  |
| country     | String            | 国家                      |
| zipcode     | String            | 邮编                      |
| timezone    | String            | 时区                      |
| accuracy    | String            | 定位精度                  |
| scene       | String            | 应用场景                  |
| asnumber    | String            | 自治域编码                |
| isp         | String            | 运营商名称                |
| owner       | String            | IP 所属机构名称           |
| multiAreas  | prov (String)     | 省份                      |
|             | city (String)     | 城市                      |
|             | district (String) | 区/县                     |
|             | lngwgs (String)   | WGS84 坐标系经度          |
|             | latwgs (String)   | WGS84 坐标系纬度          |
|             | lngbd (String)    | BD09 坐标系经度           |
|             | latbd (String)    | DB09 坐标系纬度           |
|             | radius (String)   | 定位半径                  |
| user_type   | String            | IP 使用者类型             |
| user        | String            | IP 使用者名称             |
| correctness | String            | 准确度                    |
| lazy_asn    | String            | ASN信息                   |


# 2.相关接口
相关接口具体如下所示：

"""


class PathPermissionsSchemaGenerator(OpenAPISchemaGenerator):
    """
    API路径权限结构

    需要配置 path_permissions
    如果符合 path_permissions 的条件 则展示
    """

    path_permissions = {
        'startswith': (),  # 以某一个开头
        'include': (),  # 路径在include里面
    }

    def has_path_permissions(self, path):
        # 取消权限认证
        return True

        startswith = self.path_permissions.get('startswith')
        if startswith:
            for prefix in startswith:
                if path.startswith(prefix):
                    return True
                continue

        if path in self.path_permissions.get('include'):
            return True

        return False

    def should_include_endpoint(self, path, method, view, public):
        """
        Check if a given endpoint should be included in the resulting schema.
        """
        return self.has_path_permissions(path)


class TS4in1SchemaGenerator(PathPermissionsSchemaGenerator):
    """
    TS4in1 API路径权限结构
    """

    path_permissions = {
        'startswith': ('/darkeye/domain/', '/i2p/domain/', '/zeronet/domain/'),
        'include': ('/e/goods/', '/e/goods/{meta_id}/', '/e/page/', '/e/page/{meta_id}/'),
    }


class UserRelationSchemaGenerator(PathPermissionsSchemaGenerator):
    """
    lianxiaoqian API路径权限结构
    """

    path_permissions = {
        'include': (
            '/e/spidermap/',
            '/e/goods/', '/e/goods/{meta_id}/',
            '/e/topic/', '/e/topic/{meta_id}/',
            '/e/user/', '/e/user/detail/', '/e/user/relation/'
        ),
    }


class YZNSchemaGenerator(PathPermissionsSchemaGenerator):
    """
    积极防御 云智脑 API路径权限结构
    """

    path_permissions = {
        'include': (
            '/e/spidermap/',
            '/e/page/', '/e/page/{meta_id}/',
            '/e/goods/', '/e/goods/{meta_id}/',
            '/e/topic/', '/e/topic/{meta_id}/',
            '/e/pastebin/', '/e/pastebin/{meta_id}/',
            '/e/leak/', '/e/leak/{meta_id}/',
            '/e/image/',
            '/e/ransomware/monitoring/', '/e/ransomware/monitoring/{meta_id}/',
            '/e/user/', '/e/user/detail/', '/e/user/relation/'
        ),
    }


api_info = openapi.Info(
    title="IPPLUS API 文档",
    default_version='v1',
    description=doc_desc,
)

schema_view = get_schema_view(
    api_info,
    public=True,
    # 取消权限认证
    # permission_classes=(permissions.IsAdminUser,),
    permission_classes=(permissions.AllowAny,),
)

ts4in1_schema_view = get_schema_view(
    api_info,
    generator_class=TS4in1SchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

user_relation_schema_view = get_schema_view(
    api_info,
    generator_class=UserRelationSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

yzn_schema_view = get_schema_view(
    api_info,
    generator_class=YZNSchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

api_doc_urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^swagger/V38JUY0eDhahdxLLolycCw4pC3rqC8cBhmZPu2w7z9UcjJzdtVlZfmVFJ2hXjziG/$',
        ts4in1_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^swagger/plu94L1lSlitScsBXkQL3EQSVhFNiHnhGZEIMMYzcgouY4y42wcHM9QllYBXBKGQ/$',
        user_relation_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^swagger/LXt9s3bRz3ZmNUAbQoPERyTrlRABn5BnZpoZEblMjXqen9zVZw2rohv4VgSSg2kG/$',
        yzn_schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

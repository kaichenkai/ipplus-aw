from django.conf.urls import url, include

from ipplus.apps.query.views import QueryIPV4APIView

urlpatterns = [
    url(r'^ipv4/$', QueryIPV4APIView.as_view(), name='ipv4'),
]

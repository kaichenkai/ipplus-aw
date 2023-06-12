from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views

from config.api_doc import api_doc_urlpatterns
from config.views import HomeAPIView

API_PREFIX = 'v1'
admin.site.site_header = 'IPPLUS Administration'

handler500 = 'config.views.server_error'
handler400 = 'config.views.bad_request'
handler403 = 'config.views.permission_denied'
handler404 = 'config.views.page_not_found'

urlpatterns = [
                  url(r'^$', HomeAPIView.as_view(), name='home'),
                  # Django Admin, use {% url 'admin:index' %}
                  url(settings.ADMIN_URL, admin.site.urls),

                  # docs
                  url(r'^docs/', include((api_doc_urlpatterns, 'api-docs'), namespace='api-docs')),

                  # businesses
                  url(r'^query/', include(('ipplus.apps.query.urls', 'query'), namespace='query')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += [url(f'{API_PREFIX}/', include('drf_openapi.urls'))]
urlpatterns += [
    url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
    url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
    url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
    url(r'^500/$', default_views.server_error),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
                          url(r'^__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns

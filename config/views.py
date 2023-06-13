import logging

from django.http import JsonResponse
from rest_framework import response, status
from rest_framework.views import APIView

from ipplus import __version__


class HomeAPIView(APIView):
    """IPPLUS Home Page"""

    def get(self, request):
        return response.Response({'title': 'IPPLUS', 'version': __version__, 'docs': '/docs/swagger/'})


def server_error(request, *args, **kwargs):
    """
    Generic 500 error handler.
    """
    data = {
        'error': 'Server Error (500)'
    }
    return JsonResponse(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def bad_request(request, exception, *args, **kwargs):
    """
    Generic 400 error handler.
    """
    data = {
        'error': 'Bad Request (400)'
    }
    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def permission_denied(request, exception, *args, **kwargs):
    """
    Generic 403 error handler.
    """
    data = {
        'error': 'Permission Denied (403)'
    }
    return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)


def page_not_found(request, exception, *args, **kwargs):
    """
    Generic 404 error handler.
    """
    data = {
        'error': 'Page Not Found (404)'
    }
    return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)

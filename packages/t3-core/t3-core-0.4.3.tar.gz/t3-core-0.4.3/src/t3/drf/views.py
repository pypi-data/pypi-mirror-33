import logging
from collections import OrderedDict
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from t3.util import get_response_type
from t3.util import json_traceback


log = logging.getLogger(__name__)


def enveloped_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    response = exception_handler(exc, context)
    if not response:
        response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    response.data = OrderedDict([
        ('status', get_response_type(response.status_code)),
        ('status_code', response.status_code),
        ('message', str(exc)),
        ('data', json_traceback()),
    ])

    # Remove traceback if debug is off, or we don't have a 500 error
    if not settings.DEBUG or response.status_code != 500:
        del response.data['data']
    else:
        log.error(response.data['data'])

    return response

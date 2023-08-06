__author__ = 'zhuxietong'
from rest_framework.views import exception_handler

from tools.jsonapi.response import ApiState


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        # response.data['status_code'] = response.status_code
        response.data['state']=ApiState.exception.value
        response.data['data']=None
        response.status_code = 200

    return response
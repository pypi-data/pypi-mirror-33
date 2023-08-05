# -*- coding:utf-8 -*-
from rest_framework.response import Response

from ..api.mixins import UserApiMixin
from . import serializers, models
from rest_framework import viewsets, decorators, response, status
from ..api import register
from dwebsocket.decorators import accept_websocket

__author__ = 'denishuang'




class TempFileViewSet(UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.TempFileSerializer
    queryset = models.TempFile.objects.all()
    user_field_name = 'owner'


register(__package__, 'tempfile', TempFileViewSet)

# class AsyncResultViewSet(viewsets.GenericViewSet):
#
#     @accept_websocket
#     def retrieve(self, request, *args, **kwargs):
#         from celery.result import AsyncResult
#         rs=AsyncResult(kwargs['pk'])
#         d = dict(
#             task_id=rs.task_id,
#             state=rs.state,
#             status=rs.status,
#             result=rs.status == 'FAILURE' and unicode(rs.result) or rs.result,
#             traceback=rs.traceback
#         )
#         return Response(d)
#
#
#
#
# register(__package__, 'async_result', AsyncResultViewSet, base_name='async_result')

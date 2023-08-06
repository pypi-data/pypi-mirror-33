# -*- coding:utf-8 -*-

from . import serializers, signals
from rest_framework import viewsets, decorators, response, status
from django_szuprefix.api import register
from django.contrib.auth import authenticate, login as auth_login
from rest_framework.serializers import Serializer

class UserViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

    @decorators.list_route(['post'], authentication_classes=[], permission_classes=[])
    def login(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            auth_login(request, serializer.user)
            return response.Response(self.get_serializer(serializer.user).data)
        return response.Response(serializer.errors, status=400)

    @decorators.list_route(['get'])
    def current(self, request):
        srs = signals.to_get_user_profile.send(sender=self, user=request.user, request=request)
        srs = [rs[1] for rs in srs if isinstance(rs[1], Serializer)]
        data = self.get_serializer(request.user, context={'request': request}).data
        for rs in srs:
            opt = rs.Meta.model._meta
            n = "as_%s_%s" % (opt.app_label, opt.model_name)
            data[n] = rs.data
        return response.Response(data)

    @decorators.list_route(['post'])
    def change_password(self, request):
        serializer = serializers.PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return response.Response({})
        return response.Response(serializer.errors, status=400)

    @decorators.list_route(['post', 'get'], authentication_classes=[], permission_classes=[])
    def logout(self, request):
        from django.contrib.auth import logout
        logout(request)
        return response.Response(status=status.HTTP_200_OK)

register('auth', 'user', UserViewSet, base_name='user')

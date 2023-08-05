# -*- coding:utf-8 -*-
# Auth: denishuang

default_app_config = 'django_szuprefix.api.apps.Config'

from rest_framework import serializers, routers



class newRouter(routers.DefaultRouter):
    def get_urls(self):
        urls = super(newRouter, self).get_urls()
        from .urls import urlpatterns as api_urls
        # from ..auth.urls import urlpatterns as auth_urls
        urls += api_urls  #auth_urls +
        return urls

router = newRouter()

def register(package, resource, viewset, base_name=None):
    p = "%s/%s" % (package.split(".")[-1], resource)
    router.register(p, viewset, base_name=base_name)


# autodiscover()

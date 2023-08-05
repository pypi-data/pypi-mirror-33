# -*- coding:utf-8 -*- 

from rest_framework import serializers, viewsets, mixins, decorators
from . import models


class TempFileSerializer(serializers.HyperlinkedModelSerializer):
    # file = serializers.FileField(write_only=True)

    class Meta:
        model = models.TempFile
        fields = ('url', 'name', 'file', 'id')

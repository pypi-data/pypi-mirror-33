# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from rest_framework import serializers
from . import models
from ..saas.mixins import PartySerializerMixin


class PaperSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Paper
        # fields = ('title', 'content', 'content_object', 'is_active', 'create_time')
        exclude=()

class AnswerSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        # fields = ('detail', 'performance', 'seconds')
        exclude = ('party',)
        read_only_fields = ('user', 'paper')


class StatSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Stat
        fields = ('detail',)


class PerformanceSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Performance
        fields = ('paper_id', 'score', 'detail')

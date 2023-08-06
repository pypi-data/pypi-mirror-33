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
        exclude = ('party',)
        extra_kwargs = {'user': {'read_only': True}}


class AnswerSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Answer
        # fields = ('detail', 'performance', 'seconds')
        exclude = ('party',)
        read_only_fields = ('user', 'paper')


class StatSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stat
        exclude = ('party',)
        # fields = ('detail',)


class PerformanceSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    paper_name = serializers.CharField(source="paper.__str__", label='试卷', read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", label='学生', read_only=True)

    class Meta:
        model = models.Performance
        exclude = ()
        # fields = ('paper_id', 'score', 'detail')
        extra_kwargs = {'paper': {'read_only': True}, 'party': {'read_only': True}, 'user': {'read_only': True}}

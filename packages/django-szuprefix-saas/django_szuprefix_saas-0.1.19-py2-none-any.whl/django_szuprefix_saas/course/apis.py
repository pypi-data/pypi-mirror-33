# -*- coding:utf-8 -*-
from rest_framework.decorators import list_route, detail_route
from rest_framework.serializers import ModelSerializer

from django_szuprefix.api.mixins import UserApiMixin
from django_szuprefix_saas.saas.mixins import PartyMixin, PartySerializerMixin
from .apps import Config
from rest_framework.response import Response

__author__ = 'denishuang'
from . import models, serializers
from rest_framework import viewsets, filters
from django_szuprefix.api import register
from rest_framework import status


class CourseViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    search_fields = ('name',)
    filter_fields = ('is_active','category')
    ordering_fields = ('is_active', 'title', 'create_time')


register(Config.label, 'course', CourseViewSet)


class CategoryViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    search_fields = ('name',)


register(Config.label, 'category', CategoryViewSet)


class ChapterViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer
    search_fields = ('name',)
    filter_fields = ('course',)


register(Config.label, 'chapter', ChapterViewSet)

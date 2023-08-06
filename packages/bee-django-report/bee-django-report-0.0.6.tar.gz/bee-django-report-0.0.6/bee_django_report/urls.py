#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_report'
urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^user/gender/$', views.UserGenderView.as_view(), name='user_gender'),
    url(r'^user/age/$', views.UserAgeView.as_view(), name='user_age'),
]
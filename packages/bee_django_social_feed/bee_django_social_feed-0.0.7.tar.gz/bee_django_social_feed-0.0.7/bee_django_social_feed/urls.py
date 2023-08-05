#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_social_feed'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^feeds$', views.feeds, name='feeds'),
    url(r'^feeds/new$', views.create_feed, name='create_feed'),
    # 点赞
    url(r'^feeds/(?P<feed_id>\d+)/emoji$', views.create_emoji, name='create_emoji'),
    # 评论
    url(r'^feeds/(?P<feed_id>\d+)/comment$', views.create_comment, name='create_comment')
]

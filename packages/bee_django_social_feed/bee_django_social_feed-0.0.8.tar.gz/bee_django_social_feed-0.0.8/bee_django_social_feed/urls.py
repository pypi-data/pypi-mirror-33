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
    url(r'^feeds/(?P<feed_id>\d+)/comment$', views.create_comment, name='create_comment'),

    # 美好生活的页面
    url(r'^albums$', views.albums, name='albums'),
    # 获取所有相册数据
    url(r'^get_albums$', views.get_albums, name='get_albums'),
    # 获取某个相册的数据
    url(r'^album/(?P<album_id>\d+)$', views.album, name='album'),
    # 创建相册
    url(r'^album/new$', views.create_album, name='create_album'),
    # 修改图片的描述
    url(r'^photo/(?P<album_photo_id>\d+)/update$', views.update_album_photo_note, name="update_album_photo_note"),

    # 审核用户上传的美好生活列表
    url(r'^manage_albums$', views.manage_albums, name='manage_albums'),
    url(r'^manage_album/(?P<album_id>\d+)$', views.manage_album, name='manage_album'),
]

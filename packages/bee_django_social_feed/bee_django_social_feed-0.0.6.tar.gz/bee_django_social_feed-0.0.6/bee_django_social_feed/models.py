# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Feed(models.Model):
    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='发布者')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.IntegerField(default=0, verbose_name='日志类型') # 0 普通日志，1 有内链接的日志（课件评论等）
    link_name = models.CharField(null=True, blank=True, verbose_name='链接显示名称', max_length=256)
    link_link = models.CharField(verbose_name='链接的http(s)', null=True, blank=True, max_length=256)


class FeedComment(models.Model):
    feed = models.ForeignKey(Feed)
    comment = models.TextField(verbose_name='评论')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(default=timezone.now)


class FeedEmoji(models.Model):
    feed = models.ForeignKey(Feed)
    emoji = models.IntegerField(default=0, verbose_name='感受')  # 0 赞，1 笑趴，2 哇，3 心碎，4 怒
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

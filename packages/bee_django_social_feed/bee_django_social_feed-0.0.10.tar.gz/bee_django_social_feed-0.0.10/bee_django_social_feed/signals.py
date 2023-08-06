# -*- coding:utf-8 -*-
from django.dispatch import Signal

# 笔记创建的信号
user_feed_created = Signal(providing_args=["feed_id"])

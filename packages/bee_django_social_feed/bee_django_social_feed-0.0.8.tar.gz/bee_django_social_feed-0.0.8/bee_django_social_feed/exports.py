#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.contrib.auth import get_user_model


user_model = get_user_model()

# 获取班级同学
def get_classmates(user_id):
    return user_model.objects.order_by('-created_at')

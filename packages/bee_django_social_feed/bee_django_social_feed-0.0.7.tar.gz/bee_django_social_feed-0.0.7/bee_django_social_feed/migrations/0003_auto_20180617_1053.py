# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-06-17 02:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bee_django_social_feed', '0002_feedcomment_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='link_link',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='\u94fe\u63a5\u7684http(s)'),
        ),
        migrations.AddField(
            model_name='feed',
            name='link_name',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='\u94fe\u63a5\u663e\u793a\u540d\u79f0'),
        ),
        migrations.AddField(
            model_name='feed',
            name='type',
            field=models.IntegerField(default=0, verbose_name='\u65e5\u5fd7\u7c7b\u578b'),
        ),
    ]

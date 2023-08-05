# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from bee_django_social_feed.models import Feed, FeedComment, FeedEmoji
# from django.core.serializers import serialize
from dss.Serializer import serializer
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from bee_django_social_feed.exports import get_classmates
# Create your views here.

user_model = get_user_model()

def index(request):

    return render(request, 'bee_django_social_feed/index.html', context={
    })


# 获取所有日志
def feeds(request):
    page = request.GET.get('page')

    # 依据type的值，判断是取所有日志，还是单个用户的日志，或者同班同学的
    type = request.GET.get('type')
    if type == '0':
        feeds = Feed.objects.order_by('-created_at')
    elif type == '1':
        user_id = request.GET.get('user_id')
        user = get_object_or_404(user_model, pk=user_id)
        feeds = Feed.objects.filter(publisher=user).order_by('-created_at')
    elif type == '2':
        user_id = request.GET.get('user_id')
        classmates = get_classmates(user_id)
        feeds = Feed.objects.filter(publisher__in=classmates).order_by('-created_at')
    else:
        feeds = Feed.objects.order_by('-created_at')

    paginator = Paginator(feeds, 10)
    try:
        data = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        data = []

    for e in data:
        e.emojis = e.feedemoji_set.all()
        for i in e.emojis:
            i.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.user_id)
        e.comments = e.feedcomment_set.order_by('-created_at')
        for j in e.comments:
            j.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=j.user_id)
        e.publisher_data = user_model.objects.values('id', 'username', 'first_name').get(pk=e.publisher_id)

    return JsonResponse(data={
        'feeds': serializer(data, output_type='json', datetime_format='string'),
        'page': page,
        'request_user_id': request.user.id,
    })


# 发表日志
def create_feed(request):
    if request.method == "POST":
        content = request.POST.get('content')
        new_feed = Feed.objects.create(content=content, publisher=request.user)

        feeds = [new_feed, ]
        for i in feeds:
            i.emojis = []
            i.comments = []
            i.publisher_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.publisher_id)
        return JsonResponse(data={
            'message': '发表成功',
            'new_feeds': serializer(feeds, output_type='json', datetime_format='string')
        })


# 点赞
def create_emoji(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)

        # 检查用户是否已经点过赞了
        emojis = feed.feedemoji_set.filter(user=request.user)
        if emojis.exists():
            message = '你已经点过赞了'
            new_emoji = None
        else:
            new_emoji = feed.feedemoji_set.create(user=request.user)
            message = '点赞成功'

        emojis = [new_emoji,]
        for i in emojis:
            i.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.user_id)
        return JsonResponse(data={
            'message': message,
            'new_emoji': serializer(emojis, output_type='json', datetime_format='string')
        })


# 发表对日志的评论
def create_comment(request, feed_id):
    if request.method == "POST":
        feed = get_object_or_404(Feed, pk=feed_id)

        comment_text = request.POST.get('comment')
        new_comment = feed.feedcomment_set.create(comment=comment_text, user=request.user)
        message = '评论成功'

        comments = [new_comment,]
        for i in comments:
            i.user_data = user_model.objects.values('id', 'username', 'first_name').get(pk=i.user_id)
        return JsonResponse(data={
            'message': message,
            'new_comments': serializer(comments, output_type='json', datetime_format='string')
        })
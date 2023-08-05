#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from django import template
from django.conf import settings
from django.shortcuts import reverse
from bee_django_course.exports import filter_local_datetime
from bee_django_course.utils import get_user_name

register = template.Library()


# 本地化时间
@register.filter
def local_datetime(_datetime):
    return filter_local_datetime(_datetime)


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)


# 获取视频供应商的名字
@register.filter
def get_video_provider_name():
    return settings.COURSE_VIDEO_PROVIDER_NAME


# 点播视频播放地址
@register.filter
def get_video_src(video_id):
    vid = video_id.__str__()
    return "https://p.bokecc.com/playhtml.bo?vid=" + vid + "&siteid=" + settings.COURSE_CC_USERID + "&autoStart=false&playerid=" + settings.COURSE_CC_PLAYERID + "&playertype=1"


# 用户是否学了此课程
@register.simple_tag
def has_course(user, course):
    return course.is_my_course(user)


# 课程显示状态
@register.simple_tag
def course_status(status):
    if status == 0:
        return '显示'
    else:
        return '不显示'


# 用户课程学习状态，user_course_section.status -> 文字
# 0 未开始， 1 学习中，2 通过，3 退回重修, 4 提交
@register.filter
def course_status(status):

    if status == 0:
        rc = '未开始'
    elif status == 1:
        rc = '学习中'
    elif status == 2:
        rc = '通过'
    elif status == 3:
        rc = '退回重修'
    elif status == 4:
        rc = '提交'
    else:
        rc = ''

    return rc

# 获取学生姓名，及详情链接
@register.filter
def get_name_detail(user, show_detail=True):
    user_name = get_user_name(user)
    if not show_detail:
        return user_name
    if settings.USER_DETAIL_EX_LINK:
        link = "<a href='" + settings.USER_DETAIL_EX_LINK + user.id.__str__() + "/'>" + user_name + "</a>"
    else:
        link = user_name
    return link


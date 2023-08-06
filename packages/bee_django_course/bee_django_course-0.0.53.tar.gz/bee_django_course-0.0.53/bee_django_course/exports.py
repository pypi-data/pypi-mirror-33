#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.contrib.auth.models import User


# django前台显示本地时间
def filter_local_datetime(_datetime):
    return _datetime


# 获取一个助教，所教的所有学生
def get_teach_users(mentor):
    return User.objects.all()

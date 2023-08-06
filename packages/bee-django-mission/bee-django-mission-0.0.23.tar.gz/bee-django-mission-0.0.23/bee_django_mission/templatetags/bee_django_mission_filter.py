#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template
# from bee_django_exam.utils import get_user_model, get_user_name
from bee_django_mission.exports import filter_local_datetime

register = template.Library()


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)


# 求两个值的差的绝对值
@register.filter
def multiple(a, b):
    return a * b

@register.filter
def get_int(a):
    return int(a)

#
# # 本地化时间
@register.filter
def local_datetime(_datetime):
    return filter_local_datetime(_datetime)

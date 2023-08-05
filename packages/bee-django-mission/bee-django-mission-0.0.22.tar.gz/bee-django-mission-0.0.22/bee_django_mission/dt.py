#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

import pytz, calendar, time
from datetime import datetime, tzinfo, timedelta

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')


# 获取现在时间，默认返回北京时间
def get_now(tz=LOCAL_TIMEZONE):
    now = datetime.now(tz)
    return now


# 获取今日0点时间，默认返回北京时间
def get_today(tz=LOCAL_TIMEZONE):
    now = get_now()
    today_str = now.strftime("%Y-%m-%d")
    today = datetime.strptime(today_str, "%Y-%m-%d")
    today = tz.localize(today)  # 加时区
    # print(now, today)
    return today


# 获取当周周日晚23点23分23秒
def get_current_week_range_datetime():
    today = get_today()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=7)
    end_date = end_date - timedelta(seconds=1)
    # print(start_date,end_date, '1')
    return start_date, end_date

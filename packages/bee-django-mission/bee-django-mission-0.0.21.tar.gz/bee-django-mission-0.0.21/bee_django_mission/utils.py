#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'

from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Stage, UserStage, UserMission, Mission, Line, UserLine
from .dt import get_current_week_range_datetime


# ============receiver============
# 创建user_line后，自动创建该用户对应的stage
@receiver(post_save, sender=UserLine)
def create_user_stage(sender, **kwargs):
    user_line = kwargs['instance']
    if kwargs['created']:
        user_line.check_add_user_stage(check=False)


# 创建user_stage后，自动创建该用户对应stage里的所有mission
@receiver(post_save, sender=UserStage)
def create_user_missions(sender, **kwargs):
    user_stage = kwargs['instance']
    if kwargs['created']:
        user_stage.check_add_user_mission(check=False)


# ====================
# 给某学生添加user_line，
# line_type:1-主线任务，2-周任务
# check：检查是否已有user_line，如果有，则不添加。默认检查
def check_add_user_line(user, line_type, check=True):
    if check:
        try:
            UserLine.objects.get(user=user, line__line_type=line_type)
            return None, '该学生还没有任务线，请先去添加'
        except:
            pass

    line = Line.objects.all().filter(line_type=line_type).first()
    res, msg = check_add_line_stage_to_user(line)
    if res:
        u_l = UserLine()
        u_l.line = line
        u_l.user = user
        u_l.save()
        return u_l, None
    return None, msg


# 检查是否可以给学生添加[line或stage]
# 如果line下没有stage，或stage下没有mission，则不通过
def check_add_line_stage_to_user(line=None, stage=None):
    if not line and stage:
        return False, '缺少参数'
    if line:
        stage = line.get_next_stage()
        if not stage:
            return False, '该任务线还没有阶段任务，请先去添加'
    if stage:
        mission_list = stage.mission_set.all()
        if not mission_list.exists():
            return False, '该阶段任务还没有具体任务，请先去添加'
    return True, None


# 则根据课件是否自动通过，开启下一user_stage
# manual是否为手动完成
# 返回下一个user_stage，没有为空
# def start_next_user_stage(user_stage, manual=False):
#     if user_stage.stutas in [0]:
#         return
#     # 如果任务线为不自动完成，则不更新
#     if not manual or not user_stage.user_line.line.auto_start:
#         return
#     user_line = user_stage.user_line
#     return user_line.check_add_user_stage()

# 获取学生的当周user_stage
def get_current_week_stage(user):
    _start_date, _end_date = get_current_week_range_datetime()
    try:
        user_stage = UserStage.objects.get(start_at=_start_date, end_at=_end_date, user_line__user=user)
        return user_stage
    except:
        return None


# ============
# 获取学生的任务线
def get_user_week_line(user):
    return _get_user_line(user, line_type=2)


def get_user_unlimited_line(user):
    return _get_user_line(user, line_type=1)


def _get_user_line(user, line_type):
    try:
        return UserLine.objects.get(user=user, line__line_type=line_type)

    except:
        return None


# ====================



# 给某学生添加周任务，check检查是否已有周任务，如果有，则不添加。默认检查
# def add_user_week_line(user, check=True):
#     if check:
#         try:
#             UserLine.objects.get(user=user, line__line_type=2)
#             return None
#         except:
#             pass
#     line = Line.objects.all().filter(line_type=2).first()
#     u_l = UserLine()
#     u_l.line = line
#     u_l.user = user
#     u_l.save()
#     return u_l

# def update_user_missions(user, stage_list=None):
#     # 没有指定stage，则更新学生所有未完成任务
#     if not stage_list:
#         user_stage_list = UserStage.objects.filter(user=user, finish_at__isnull=True)
#         stage_list = []
#         for s in user_stage_list:
#             try:
#                 stage = Stage.objects.get(id=s.stage.id)
#                 stage_list.append(stage)
#             except:
#                 continue

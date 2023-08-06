#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_mission'
urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.MissionList.as_view(), name='index'),
    # ======stage========
    url(r'^stage/unlimited/list/$', views.StageUnlimitedList.as_view(), name='stage_unlimited_list'),
    # url(r'^detail/(?P<pk>[0-9]+)/$', views.StageDetail.as_view(), name='mission_detail'),
    url(r'^stage/add/(?P<line_id>[0-9]+)/$', views.StageCreate.as_view(), name='stage_add'),
    url(r'^stage/update/(?P<pk>[0-9]+)/$', views.StageUpdate.as_view(), name='stage_update'),
    # url(r'^delete/(?P<pk>[0-9]+)/$', views.MissionDelete.as_view(), name='mission_delete'),

    # ===== mission======
    url(r'^list/$', views.MissionList.as_view(), name='mission_list'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.MissionDetail.as_view(), name='mission_detail'),
    url(r'^add/(?P<line_type>[0-9]+)/$', views.MissionCreate.as_view(), name='mission_add'),
    url(r'^update/(?P<line_type>[0-9]+)/(?P<pk>[0-9]+)/$', views.MissionUpdate.as_view(), name='mission_update'),
    url(r'^delete/(?P<pk>[0-9]+)/$', views.MissionDelete.as_view(), name='mission_delete'),




    # ===user line ====
    url(r'^user/line/create/(?P<user_id>[0-9]+)/$', views.UserLineCreate.as_view(),
        name='user_line_add'),

    # ======user stage =====
    url(r'^user/stage/detail/(?P<pk>[0-9]+)/$', views.UserStageDetail.as_view(),
        name='user_stage_detail'),
    url(r'^user/stage/update/status/(?P<user_stage_id>[0-9]+)/(?P<status>[0-9]+)/$',
        views.UserStageUpdateStatus.as_view(), name='user_stage_update_status'),
    url(r'^user/stage/update/mission/(?P<user_stage_id>[0-9]+)/$', views.UserStageUpdateMission.as_view(),
        name='user_stage_update_mission'),


    # ====user mission =====
    # 获取学生的周任务
    url(r'^user/mission/list/week/(?P<user_id>[0-9]+)/$', views.UserMissionListWeek.as_view(), name='user_line_week'),
    # 获取学生的长线任务
    url(r'^user/mission/list/unlimited/(?P<user_id>[0-9]+)/$', views.UserMissionListUnlimited.as_view(),
        name='user_line_unlimited'),
    url(r'^user/mission/update/(?P<pk>[0-9]+)/$', views.UserStageUpdate.as_view(), name='user_stage_update'),

    # ==== user stage finish count ======
    url(r'^user/stage/finish/rank/list/(?P<line_id>[0-9]+)/$', views.UserStageFinishRankList.as_view(), name='user_stage_finish_rank_list'),
]

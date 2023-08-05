# coding=utf-8
__author__ = 'zhangyue'
import os, datetime, urllib2, json
from django.core.management.base import BaseCommand, CommandError
from bee_django_mission.models import ContentType, MissionType, Line, Stage


class MissionTypeData():
    mission_type_list = [
        {
            "id": 0,
            'name': '直播时长',
            "field_name": "duration",
            "conditions": "status:1",
            "aggragate_type": 2,
            "comparison_type": 1,
            'timestamp_field': "start_time",
            "operator_type": 1,
            "link_url": "/custom_course/user_live/",
            "link_name": "去直播"
        },
        {
            "id": 1,
            'name': '转介人数',
            "field_name": "id",
            "conditions": "level:3",
            "aggragate_type": 1,
            "comparison_type": 1,
            'timestamp_field': "created_at",
            "operator_type": 0,
            "link_url": "",
            "link_name": ""
        },
        {
            "id": 2,
            'name': '考级通过',
            "field_name": "id",
            "conditions": "status:1",
            "aggragate_type": 1,
            "comparison_type": 1,
            "timestamp_field": None,
            "operator_type": 0,
            "link_url": "",
            "link_name": ""
        },
        {
            "id": 3,
            'name': '直播天数',
            "field_name": "start_time",
            "conditions": "status:1",
            "aggragate_type": 3,
            "comparison_type": 1,
            'timestamp_field': "start_time",
            "operator_type": 0,
            "link_url": "/custom_course/user_live/",
            "link_name": "去直播"
        },
        {
            "id": 4,
            'name': '完成课程课件',
            "field_name": "id",
            "conditions": "finished_at__isnull:False",
            "aggragate_type": 1,
            "comparison_type": 1,
            "timestamp_field": None,
            "operator_type": 0,
            "link_url": "/course/user_course/",
            "link_name": "去学习"
        },

    ]
    content_type_list = [
        {
            "app_label": "bee_django_course",
            "model": 'UserLive',
            'user_field': 'user',
            "info": '课程-习琴记录表',
            'mission_list': [
                mission_type_list[0], mission_type_list[3]
            ]
        },
        {
            "app_label": "bee_django_crm",
            "model": 'PreUser',
            'user_field': 'referral_user',
            "info": 'crm-转介记录表',
            'mission_list': [
                mission_type_list[1]
            ]
        },
        {
            "app_label": "bee_django_exam",
            "model": 'UserExamRecord',
            'user_field': 'user',
            "info": '考级-考级记录表',
            'mission_list': [
                mission_type_list[2]
            ]
        },
        {
            "app_label": "bee_django_course",
            "model": 'UserCourseSection',
            'user_field': 'user_course__user',
            "info": '课程-学生学习课件表',
            'mission_list': [
                mission_type_list[4]
            ]
        },
    ]


class lineDate():
    line_list = [
        {"name": "里程碑",
         "line_type": 1,
         "auto_finish": 0,
         "auto_start": 1
         },
        {"name": "周任务",
         "line_type": 2,
         "auto_finish": 1,
         "auto_start": 0
         },
    ]


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.init_mission_type()
        self.init_line()
        self.init_stage()

    def init_line(self):
        line_list = lineDate.line_list
        for line in line_list:
            self.save_line(line)
        return

    def save_line(self, line):
        name = line['name']
        line_type = line['line_type']
        auto_finish = line['auto_finish']
        auto_start = line['auto_start']
        try:
            l = Line.objects.get(name=name)

        except:
            l = Line()
            l.name = name
            l.line_type = line_type
            l.auto_finish = auto_finish
            l.auto_start = auto_start
            l.save()
        return l

    def init_stage(self):
        stage_name = '本周任务'
        try:
            l = Line.objects.get(line_type=2)
            pass
        except:
            return
        try:
            Stage.objects.get(name=stage_name)
            return
        except:
            pass
        stage = Stage()
        stage.name = stage_name
        stage.level = 1
        stage.line = l
        stage.save()
        return stage

    def init_mission_type(self):
        content_type_list = MissionTypeData.content_type_list
        for content_type in content_type_list:
            ct = self.save_content_type(content_type)
            # print(ct)
            mission_list = content_type['mission_list']
            for mission_type in mission_list:
                self.save_mission_type(mission_type, ct)
        return

    def save_content_type(self, content_type):
        app_label = content_type['app_label']
        model = content_type['model']
        user_field = content_type['user_field']
        info = content_type['info']
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except:
            ct = ContentType()
            ct.app_label = app_label
            ct.model = model
            ct.user_field = user_field
            ct.info = info
            ct.save()
        return ct

    def save_mission_type(self, mission_type, ct):
        name = mission_type["name"]
        field_name = mission_type["field_name"]
        conditions = mission_type["conditions"]
        aggregate_type = mission_type["aggragate_type"]
        comparison_type = mission_type["comparison_type"]
        timestamp_field = mission_type["timestamp_field"]
        operator_type = mission_type["operator_type"]
        link_url = mission_type["link_url"]
        link_name = mission_type["link_name"]
        try:
            mt = MissionType.objects.get(name=name)
        except:
            mt = MissionType()
        mt.name = name
        mt.field_name = field_name
        mt.conditions = conditions
        mt.aggregate_type = aggregate_type
        mt.comparison_type = comparison_type
        mt.timestamp_field = timestamp_field
        mt.operator_type = operator_type
        mt.content_type = ct
        mt.link_name = link_name
        mt.link_url = link_url
        mt.save()
        return mt

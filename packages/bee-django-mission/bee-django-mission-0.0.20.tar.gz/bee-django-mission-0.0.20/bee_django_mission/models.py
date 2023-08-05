# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime, random

from django.db import models
from django.db.models import Count, Sum, Max, Min
from django.db.models.functions import TruncMonth, TruncDay
from django.core.urlresolvers import reverse
from django.conf import settings
from django.apps import apps
from django.utils import timezone

from .dt import get_current_week_range_datetime, get_now, LOCAL_TIMEZONE
from .signals import add_prize_coin


# Create your models here.

class ContentType(models.Model):
    app_label = models.CharField(max_length=180, verbose_name='app名')
    model = models.CharField(max_length=180, verbose_name='模块名')
    user_field = models.CharField(max_length=180, verbose_name='用户字段名')
    info = models.CharField(max_length=180, verbose_name='备注', null=True)

    class Meta:
        db_table = 'bee_django_mission_content_type'
        app_label = 'bee_django_mission'
        ordering = ['id']
        unique_together = ("app_label", 'model')

    def __str__(self):
        return self.app_label + '.' + self.model


LINE_TYPE_CHOICES = ((1, "长期任务"), (2, '周任务'))


class Line(models.Model):
    name = models.CharField(max_length=180, verbose_name='标题')
    created_at = models.DateTimeField(auto_now_add=True)
    line_type = models.IntegerField(default=0, choices=LINE_TYPE_CHOICES)
    auto_finish = models.BooleanField(default=True, verbose_name='是否自动完成')
    auto_start = models.BooleanField(default=True, verbose_name='是否自动开启下一个')

    class Meta:
        db_table = 'bee_django_mission_line'
        app_label = 'bee_django_mission'
        ordering = ['id']
        verbose_name = '任务线'
        permissions = (
            ('can_manage_mission', '可以进入mission管理页'),
        )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    # 获取下一个stage，如stage为空，则获取第一个stage，没有返回空
    def get_next_stage(self, current_stage=None):
        if current_stage:
            current_stage_level = current_stage.level
        else:
            current_stage_level = 0
        next_stage_list = self.stage_set.filter(level__gt=current_stage_level).order_by("level")
        if next_stage_list.count() > 0:
            next_stage = next_stage_list.first()
            return next_stage
        else:
            return None

    def is_week_line(self):
        return self.line_type == 2

    def is_unlimited_line(self):
        return self.line_type == 1


class Stage(models.Model):
    line = models.ForeignKey(Line, on_delete=models.SET_NULL, null=True)
    level = models.IntegerField(verbose_name='阶段', null=True)
    name = models.CharField(max_length=180, verbose_name='标题')
    created_at = models.DateTimeField(auto_now_add=True)
    prize_min = models.IntegerField(default=0, verbose_name="奖励m币下限")  # 奖励m币下限
    prize_max = models.IntegerField(default=0, verbose_name='奖励m币上限')  # 奖励m币上限

    class Meta:
        unique_together = ("line", "level")
        db_table = 'bee_django_mission_stage'
        app_label = 'bee_django_mission'
        ordering = ['level']
        verbose_name = '阶段任务'

    def get_absolute_url(self):
        return reverse('bee_django_mission:stage_unlimited_list')

    def __str__(self):
        return self.line.name + "-" + self.name

    def __unicode__(self):
        return self.line.name + "-" + self.name

    @classmethod
    def get_week_stage(cls):
        try:
            return cls.objects.get(line__line_type=2)
        except:
            return


MISSION_AGGREGATE_TYPE_CHOICES = ((1, "Count"), (2, "Sum"), (3, "TruncDay"))
MISSION_COMPARISON_TYPE_CHOICES = ((1, '>='), (2, '>'))
MISSION_OPERATOR_TYPE_CHOICES = ((0, '无'), (1, '* 60'),)
MISSION_LINK_TYPE_CHOICES = ((0, '无'), (1, 'url后面接user.id'),)


class MissionType(models.Model):
    name = models.CharField(max_length=180, verbose_name='标题', unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, verbose_name='app及model')
    aggregate_type = models.IntegerField(default=1, choices=MISSION_AGGREGATE_TYPE_CHOICES,
                                         verbose_name='聚合类型')  # max/count/sum
    field_name = models.CharField(max_length=180, default='id', verbose_name='取值字段名')
    timestamp_field = models.CharField(max_length=180, verbose_name='时间字段名', null=True, blank=True)
    comparison_type = models.IntegerField(verbose_name='比较类型', choices=MISSION_COMPARISON_TYPE_CHOICES,
                                          default=1)  # 大于等于小于
    operator_type = models.IntegerField(verbose_name='对值运算', choices=MISSION_OPERATOR_TYPE_CHOICES,
                                        default=0)
    conditions = models.TextField(verbose_name='其他附加条件', help_text='格式为：[条件1：值1，条件2：值2]，多个条件用,分割', null=True,
                                  blank=True)

    link_url = models.CharField(max_length=180, null=True, blank=True, verbose_name='链接地址')
    link_name = models.CharField(max_length=180, null=True, blank=True, verbose_name='链接名字')
    line_type = models.IntegerField(verbose_name='对值运算', choices=MISSION_LINK_TYPE_CHOICES,
                                    default=0)

    class Meta:
        db_table = 'bee_django_mission_type'
        app_label = 'bee_django_mission'
        ordering = ['id']
        verbose_name = u'任务类型'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Mission(models.Model):
    mission_type = models.ForeignKey(MissionType, on_delete=models.SET_NULL, null=True, verbose_name='任务类型')
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, verbose_name='所属阶段')
    name = models.CharField(max_length=180, verbose_name='标题')
    count = models.IntegerField(verbose_name='要求数量')
    info = models.TextField(verbose_name='备注', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_by = models.IntegerField(verbose_name='顺序', null=True, blank=True)

    class Meta:
        db_table = 'bee_django_mission'
        app_label = 'bee_django_mission'
        ordering = ['created_at']
        verbose_name = '任务'

    def get_absolute_url(self):
        return reverse('bee_django_mission:mission_list')

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class UserLine(models.Model):
    line = models.ForeignKey(Line)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    start_at = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'bee_django_mission_user_line'
        app_label = 'bee_django_mission'
        ordering = ['start_at']
        verbose_name = '学生任务线'

    def __str__(self):
        return self.line.name

    def __unicode__(self):
        return self.line.name

    # 获取该学生，同一user_line下，最后的user_stage，没有返回空
    def get_last_user_stage(self, status_list=None):
        user_stage_list = UserStage.objects.filter(user_line=self).order_by(
            'created_at')
        if status_list:
            user_stage_list = user_stage_list.filter(stutas__in=status_list)
        if user_stage_list.count() > 0:
            return user_stage_list.last()
        else:
            return None

    # 获取该学生，同一user_line下的所有stage
    def get_user_all_stage(self):
        user_stage_list = UserStage.objects.filter(user_line=self).order_by(
            'created_at')
        return user_stage_list

    # 获取该学生，同一user_line下，正在进行的user_stage，没有返回空
    def get_woking_user_stage(self):
        woking_user_stage_list = UserStage.objects.filter(user_line=self, stutas=0).order_by(
            'finish_at')
        if woking_user_stage_list.count() >= 1:
            return woking_user_stage_list.last()
        else:
            return None

    # 添加user_line下的所有stage
    # user_line：要添加的user_line
    # check：检查是否有未完成的stage
    # 返回新添加的user_stage
    def check_add_user_stage(self, check=True):
        # 已经有未完成的stage
        if check:
            woking_stage = self.get_woking_user_stage()
            if woking_stage:
                return
        return self.add_user_stage()

    # 添加user_stage 返回新添加的user_stagae
    def add_user_stage(self):
        # 找到第一个,或最后一个user_stage，包括已完成和未完成
        if self.line.is_unlimited_line():
            last_user_stage = self.get_last_user_stage(status_list=[1, 2])
            if last_user_stage:
                last_stage = last_user_stage.stage
            else:
                last_stage = None
            next_stage = self.line.get_next_stage(last_stage)
        elif self.line.is_week_line():
            next_stage = Stage.get_week_stage()
        else:
            next_stage = None

        # 添加阶段任务
        if next_stage:
            # 如果该stage下还未添加mission，则不添加
            mission_list = next_stage.mission_set.all()
            if not mission_list.exists():
                return

            new_user_stage = UserStage()
            new_user_stage.user_line = self
            new_user_stage.stage = next_stage
            # 如果是周任务，添加结束时间
            if self.line.is_week_line():
                start_dt, end_dt = get_current_week_range_datetime()
                new_user_stage.start_at = start_dt
                new_user_stage.end_at = end_dt
                new_user_stage.name = start_dt.strftime("%Y") + '年第' + start_dt.strftime("%W") + "周任务"

            new_user_stage.save()
        else:
            return None
        return new_user_stage


USERSTAGE_STUTAS_CHOICES = ((0, '进行中'), (1, '已完成'), (2, '未完成'), (3, '可完成但未完成'))


class UserStage(models.Model):
    user_line = models.ForeignKey(UserLine)
    stage = models.ForeignKey(Stage)
    name = models.CharField(max_length=180, null=True, verbose_name='标题')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    start_at = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    finish_at = models.DateTimeField(null=True, verbose_name='完成时间')
    end_at = models.DateTimeField(null=True, verbose_name='结束时间')
    stutas = models.IntegerField(default=0, verbose_name='状态')
    prize_coin = models.IntegerField(default=0, verbose_name='奖励的m币')

    class Meta:
        db_table = 'bee_django_mission_user_stage'
        app_label = 'bee_django_mission'
        ordering = ['start_at']
        verbose_name = '学生阶段任务'

    def __str__(self):
        return self.stage.name

    def get_name(self):
        if self.name:
            return self.name
        return self.stage.name

    def check_add_user_mission(self, check=True):
        self.add_user_mission()

    # 添加当前user_stage下的所有mission，如果已添加，则不重复添加
    # 单个任务如有自定义模版，则按照模版规则添加
    def add_user_mission(self):
        # 所有user_stage下的mission
        mission_list = Mission.objects.filter(stage=self.stage)

        for mission in mission_list:
            # 已经添加过该mission
            try:
                UserMission.objects.get(mission=mission, user_stage=self)
            except:
                pass

            new_user_misssion = UserMission()
            new_user_misssion.user_stage = self
            new_user_misssion.mission = mission
            # 查看学生自定义任务模版，如果有，则更改为自定义任务
            try:
                custom_mission = CustomUserMission.objects.get(user=self.user_line.user, stage=self.stage,
                                                               mission=mission)
                new_user_misssion.custom_name = custom_mission.custom_name
                new_user_misssion.custom_count = custom_mission.custom_count
            except:
                pass
            new_user_misssion.save()
        return

    # 更新该user_stage下，所有的mission完成情况
    def update_user_mission(self):
        # 所有未完成的user_mission
        user_mission_list = self.usermission_set.filter(finish_at__isnull=True)
        for user_mission in user_mission_list:
            user_mission.get_user_mission_progress()
        return

    # 更新user_stage状态，检查进行中的，是否可以改变状态
    def update_user_stage_status(self):
        if self.stutas in [1, 2, 3]:
            return self.stutas

        unfinish_list = UserMission.objects.filter(user_stage=self, finish_at__isnull=True)
        # 所有mission都已完成
        if unfinish_list.count() == 0:
            if self.user_line.line.auto_finish:
                self.finish_user_stage_add_prize()
            else:

                self.stutas = 3
        # 还有mission未完成
        else:
            # 如果是周任务，且过期
            if self.user_line.line.is_week_line() and self.end_at < get_now():
                self.stutas = 2
        self.save()
        return self.stutas

    def finish_user_stage_add_prize(self):
        self.finish_at = get_now()
        self.stutas = 1
        coin = random.randint(self.stage.prize_min, self.stage.prize_max)
        reason = '完成任务奖励'
        if self.user_line.line.is_week_line():

            reason = '完成' + self.start_dt.strftime("%Y") + '年第' + self.start_dt.strftime("%W") + "周任务奖励"

        elif self.user_line.line.is_unlimited_line():
            reason = '完成' + self.get_name() + "任务奖励"
        add_prize_coin.send(sender=UserStage, user=self.user_line.user, coin=coin, reason=reason)
        self.prize_coin = coin
        self.save()
        self.update_finish_count()

    # 更新user_mission为最新的stage中的mission
    def update(self):
        stage = self.stage
        user = self.user_line.user
        mission_list = Mission.objects.filter(stage=stage)
        for mission in mission_list:
            # 检查重复，没有则创建
            try:
                UserMission.objects.get(mission=mission, user_stage=self)
                continue
            except:
                user_mission = UserMission()
                user_mission.user = user
                user_mission.mission = mission
                user_mission.user_stage = self
                user_mission.save()

        return

    # 更新用户完成阶段任务的数量，用于排行榜
    def update_finish_count(self):
        user = self.user_line.user
        line = self.user_line.line
        user_finish_stage_list = UserStage.objects.filter(user_line__user=user,
                                                          user_line__line__line_type=line.line_type,
                                                          stutas=1)
        count = user_finish_stage_list.count()
        try:
            user_count = UserStageFinishCount.objects.get(user=user, line=line)
        except:
            user_count = UserStageFinishCount()
            user_count.user = user
            user_count.line = line
        user_count.finish_count = count
        user_count.save()
        return


# 自定义学生任务模版
class CustomUserMission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    stage = models.ForeignKey(Stage)
    mission = models.ForeignKey(Mission)
    custom_name = models.CharField(max_length=180, blank=True, null=True, verbose_name='自定义名字')
    custom_count = models.IntegerField(blank=True, null=True, verbose_name='自定义数量')

    class Meta:
        db_table = 'bee_django_mission_custom_user_mission'
        app_label = 'bee_django_mission'
        ordering = ['pk']
        verbose_name = '学生自定义任务'

    def __str__(self):
        return self.stage.name


class UserMission(models.Model):
    # line = models.ForeignKey(Line)
    user_stage = models.ForeignKey(UserStage)
    mission = models.ForeignKey(Mission)
    custom_name = models.CharField(max_length=180, blank=True, null=True, verbose_name='自定义名字')
    custom_count = models.IntegerField(blank=True, null=True, verbose_name='自定义数量')
    # user = models.ForeignKey(settings.AUTH_USER_MODEL)
    finish_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'bee_django_mission_user_mission'
        app_label = 'bee_django_mission'
        ordering = ['finish_at']
        verbose_name = '学生的任务'
        permissions = ('can_reset_user_mission', '可以重置学生的任务'),

    def __str__(self):
        return self.mission.name

    def __unicode__(self):
        return self.mission.name

    def get_name(self):
        if self.custom_name:
            return self.custom_name
        return self.mission.name

    def get_count(self):
        if self.custom_count == None:
            return self.mission.count
        else:
            return self.custom_count

    def get_link(self):
        mission_type = self.mission.mission_type
        if mission_type.link_url:
            if mission_type.line_type == 0:
                return mission_type.link_url
            if mission_type.line_type == 1:
                return mission_type.link_url + self.user_stage.user_line.user.id.__str__()

    # 获取user_mission的完成情况
    # 返回【是否完成，已完成，要求，百分比】
    def get_user_mission_progress(self):
        operator_type = self.mission.mission_type.operator_type  # 对count做运算
        count = self.get_count()
        # 前台显示用
        show_require = count
        if operator_type == 1:
            count = count * 60
        # print(count,show_require)
        # if self.finish_at:
        #     return True, show_require, show_require, 100
        # 表
        content_type = self.mission.mission_type.content_type
        app_name = content_type.app_label
        model_name = content_type.model
        app = apps.get_app_config(app_name)
        model = app.get_model(model_name)
        # print(app, model)
        # 查询条件
        user_field = content_type.user_field
        aggregate_type = self.mission.mission_type.aggregate_type
        field_name = self.mission.mission_type.field_name
        timestamp_field = self.mission.mission_type.timestamp_field
        comparison_type = self.mission.mission_type.comparison_type  # 大于等于小于
        conditions = self.mission.mission_type.conditions

        # 查询
        try:
            queryset = model.objects.all()
            if queryset.count() == 0:
                return False, 0, show_require, 0
            # print(queryset)
            kwargs = {}  # 动态查询的字段
            # name_field = get_user_name_field()
            kwargs[user_field] = self.user_stage.user_line.user
            if conditions:
                condition_list = conditions.split(',')
                # print(condition_list)
                for condition in condition_list:
                    # print(condition)
                    key = condition.split(':')[0]
                    value = condition.split(':')[1]
                    kwargs[key] = value
            # 周任务
            if self.user_stage.user_line.line.is_week_line():
                kwargs[timestamp_field + "__range"] = [self.user_stage.start_at, self.user_stage.end_at]

            # print(kwargs)
            queryset = queryset.filter(**kwargs)
            if queryset.count() == 0:
                return False, 0, show_require, 0
            # print(queryset)
            # 聚合查询
            if aggregate_type == 1:  # count
                queryset = queryset.aggregate(_agg=Count(field_name))
            elif aggregate_type == 2:  # sum
                queryset = queryset.aggregate(_agg=Sum(field_name))
            elif aggregate_type == 3:  # TruncDay
                _queryset = queryset.annotate(day=TruncDay(field_name, tzinfo=LOCAL_TIMEZONE)).values('day').annotate(
                    count=Count('id')).values('day') \
                    .order_by('day')
                queryset = {}
                queryset["_agg"] = _queryset.count()

            else:
                return False, 0, 0
            # 比较
            if comparison_type == 1:
                res = queryset["_agg"] >= count
            elif comparison_type == 2:
                res = queryset["_agg"] > count
            else:
                res = None
            # print(res)
            if operator_type == 1:
                show_finish = 0
            else:
                show_finish = queryset["_agg"]
            if show_require == 0:
                percent = 100
            else:
                percent = show_finish * 100 / show_require
            if self.finish_at:
                return True, show_finish, show_require, percent
            else:
                if res:
                    # print('finished')
                    self.finish_at = get_now()
                    self.save()
                    return True, show_finish, show_require, percent
                else:

                    # print(queryset["_agg"])
                    # print('not finished')
                    return False, show_finish, show_require, percent


        except Exception as e:
            print(e)
        return False, 0, 0


class UserStageFinishCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    finish_count = models.IntegerField(default=0)
    line = models.ForeignKey(Line)

    def __str__(self):
        return self.user + ":count:" + self.finish_count.__str__()

    def __unicode__(self):
        return self.user + ":count:" + self.finish_count.__str__()

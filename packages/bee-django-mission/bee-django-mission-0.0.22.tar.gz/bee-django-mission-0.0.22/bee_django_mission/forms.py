# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from django.core.exceptions import NON_FIELD_ERRORS

from .models import Mission, Stage, UserLine, Line, UserMission
from .utils import check_add_line_stage_to_user


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['line', "name", 'level', 'prize_min', 'prize_max']
        unique_together = ("line", "level")
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "阶段不能重复",
            }
        }


class StageUnlimitedForm(StageForm):
    l = Line.objects.filter(line_type=1)
    line = forms.ModelChoiceField(queryset=l, label='所属任务线', required=True)



    # def validate_unique(self):
    #     exclude = self._get_validation_exclusions()
    #     # exclude.remove('level') # allow checking against the missing attribute
    #
    #     try:
    #         self.instance.validate_unique(exclude=exclude)
    #     except forms.ValidationError, e:
    #         self._update_errors(e.message_dict)

    # def clean(self):
    #     level = self.cleaned_data['level']
    #     print(self)
    #     stage_list = Stage.objects.filter(level=level, line__line_type=1)
    #     if stage_list.exists():
    #         raise forms.ValidationError(u"阶段不能重复")
    #     return self.cleaned_data


class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ['mission_type', "stage", "name", "count", "info", 'order_by']

    def __init__(self, line, *args, **kwargs):
        super(MissionForm, self).__init__(*args, **kwargs)
        stage_queryset = Stage.objects.filter(line=line)
        self.fields["stage"] = forms.ModelChoiceField(queryset=stage_queryset, label='所属阶段', required=True)


class UserLineCreateForm(forms.ModelForm):
    class Meta:
        model = UserLine
        fields = ['line']

    def __init__(self, *args, **kwargs):
        super(UserLineCreateForm, self).__init__(*args, **kwargs)
        line_queryset = Line.objects.filter(line_type=1)
        self.fields["line"] = forms.ModelChoiceField(queryset=line_queryset, label='任务线', required=True)

    def clean(self):
        line = self.cleaned_data['line']
        res, msg = check_add_line_stage_to_user(line)
        if not res:
            raise forms.ValidationError(msg)
        return self.cleaned_data


class UserMissionForm(forms.ModelForm):
    class Meta:
        model = UserMission
        fields = ['custom_name', 'custom_count']

    def __init__(self, *args, **kwargs):
        super(UserMissionForm, self).__init__(*args, **kwargs)
        if not self.initial["custom_name"]:
            self.initial["custom_name"] = self.instance.mission.name
        if not self.initial["custom_count"]:
            self.initial["custom_count"] = self.instance.mission.count

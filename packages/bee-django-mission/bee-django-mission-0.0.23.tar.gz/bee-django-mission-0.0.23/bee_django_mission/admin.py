# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ContentType, Line, Stage, MissionType,Mission
# Register your models here.
admin.site.register(ContentType)
admin.site.register(Line)
admin.site.register(Stage)
admin.site.register(MissionType)
admin.site.register(Mission)

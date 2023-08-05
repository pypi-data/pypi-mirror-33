#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import json
from django.http import HttpResponse


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")
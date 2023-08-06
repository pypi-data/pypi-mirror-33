# -*- coding:utf-8 -*-
from django.http import JsonResponse


class JsonSuccessResponse(JsonResponse):
    def __init__(self, data, **kwargs):
        data['code'] = 0
        super().__init__(data, **kwargs)


class JsonFailResponse(JsonResponse):
    def __init__(self, data, **kwargs):
        if 'code' not in data:
            data['code'] = 1
        super().__init__(data, **kwargs)

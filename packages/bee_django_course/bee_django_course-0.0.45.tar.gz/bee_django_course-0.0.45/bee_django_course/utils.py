# -*- coding: utf-8 -*-
__author__ = 'bee'

import urllib, urllib2, pytz, json
from django.http import HttpResponse
from datetime import datetime
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')


# =====http====
def http_get(url):
    f = urllib.urlopen(url)
    s = f.read()
    return s


def http_post(url, parameters=None):
    parameters = urllib.urlencode(parameters)
    request = urllib2.Request(url, parameters)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    res_data = urllib2.urlopen(request, timeout=10)
    res = res_data.read()
    return res


# ====dt====
# 获取本地当前时间
def get_now(tz=LOCAL_TIMEZONE):
    return datetime.now(tz)


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")


def page_it(request, query_set, url_param_name='page', items_per_page=25):
    paginator = Paginator(query_set, items_per_page)

    page = request.GET.get(url_param_name)
    try:
        rs = paginator.page(page)
    except PageNotAnInteger:
        rs = paginator.page(1)
    except EmptyPage:
        rs = paginator.page(paginator.num_pages)

    return rs
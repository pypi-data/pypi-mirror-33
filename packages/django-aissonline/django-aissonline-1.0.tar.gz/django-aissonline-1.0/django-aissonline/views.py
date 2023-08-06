import requests as http_unit
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
from django.views.decorators.cache import cache_page

HEADER = {
    'Host': 'api.pmkoo.cn',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'User-Agent': 'aiss/1 CFNetwork/901.1 Darwin/17.6.0',
    'Accept-Language': 'zh-cn',
}

AISS_CONFIG = {}


@cache_page(24 * 60 * 60)
def aiss_config(request, **kwargs):
    """
    获取aiss APP url 配置
    :return: url config
    """
    respones_json = http_unit.post('http://api.pmkoo.cn/aiss/system/config.do', headers=HEADER).json()
    global AISS_CONFIG
    AISS_CONFIG = respones_json
    respones = JsonResponse(respones_json)
    respones["Access-Control-Allow-Origin"] = "*"
    return respones


@cache_page(1 * 60 * 60)
def suite_list(request, **kwargs):
    """
    获取套图列表
    :param request:
    :return:
    """
    respones_json = http_unit.post('http://api.pmkoo.cn/aiss/suite/suiteList.do', headers=HEADER, data=kwargs).json()
    respones = JsonResponse(respones_json)
    respones["Access-Control-Allow-Origin"] = "*"
    return respones


@cache_page(24 * 60 * 60)
def index(request, **kwargs):
    return HttpResponseRedirect('/static/aissonline/aissindex.html')

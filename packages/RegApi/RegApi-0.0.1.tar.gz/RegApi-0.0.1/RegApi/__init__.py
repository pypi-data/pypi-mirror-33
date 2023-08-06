# coding: utf-8
"""RegApi"""
import json
import urllib3
from urllib import request
from .base import RegRuBase


class RegRuApiDomain(object):
    """Domains"""
    def __init__(self):
        self.path_prefix = '/domain/'
        self.path_postfix = '?'

    def get_api(self, params, action):
        """Получаем функцию у регру"""
        reg_ru = RegRuBase()
        api_path_dir = self.path_prefix + action + self.path_postfix

        response = request.urlopen(reg_ru.generate_api_url(api_path_dir, params))

        jdata = response.read().decode('utf8')

        # print(RegRu.checkCurrentErrors(jdata))

        if reg_ru.check_current_errors(jdata) == 1:
            return json.loads(jdata)
        return reg_ru.check_current_errors(jdata)

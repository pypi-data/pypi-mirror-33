# coding: utf-8
"""RegAPi"""
from urllib.parse import urlencode
from RegApi.errors import REGRUERRORS


class RegRuBase(object):
    '''Базовый класс'''
    def __init__(self):
        self.api_path = 'https://api.reg.ru/api/regru2'

    def parse_error(self, error_code):
        """Парсим стандартные ошибки. На вход передаем то, что у нас вернулось от АПИ"""
        results = 'Unspecified error'
        if error_code in REGRUERRORS:
            results = REGRUERRORS[error_code]
        return results

    def check_current_errors(self, variables):
        """Общая проверка на ошибки"""
        if 'error_code' in variables:
            return self.parse_error(variables['error_code'])
        return 1

    def generate_api_url(self, api_path_dir, params):
        """Генерируем общий путь до функции"""
        return self.api_path + api_path_dir + urlencode(params)

# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     api
   Description :
   Author :       潘晓华
   date：          2018/7/2
-------------------------------------------------
"""

import base64
import requests
import re
import time

from config import Config
from .token_cache import token_cache
import json
import urllib3
urllib3.disable_warnings()

class Api(object):
    """
    Openshift Api
    """
    @classmethod
    def get_token(cls):
        """
        获取token
        :return: token
        """
        token = token_cache.get()
        if not token:
            base64_string = base64.encodestring('%s:%s' % (Config.OPENSHIFT_USER, Config.OPENSHIFT_PASSWD)).strip()
            header = {"Authorization": "Basic %s" % base64_string}
            result = requests.get(
                Config.OPENSHIFT_URL + '/oauth/authorize?response_type=token&client_id=openshift-challenging-client',
                headers=header, verify=False, allow_redirects=False)
            token_data = re.search(r'#access_token=([^&]*)&expires_in=([^&]*)&' ,result.headers['Location']).groups()
            token_cache.set(token_data[0], int(time.time()) + int(token_data[1]) - 300)
            token = token_data[0]
        return token

    @classmethod
    def request(cls, method='get', url='', params=None, data=None):
        header = {"Authorization": "Bearer %s" % cls.get_token()}
        url = '%s/%s/%s' % (Config.OPENSHIFT_URL, cls.api_version, url)
        result = requests.request(method, url, headers=header, verify=False, params=params, data=data)
        return json.loads(result.content)



    @classmethod
    def get(cls, url='', params=None):
        return cls.request('get', url, params)

    @classmethod
    def post(cls, url='', params=None):
        return cls.request('post', url, params)

class K8s_Api(Api):
    api_version = 'api/v1'


class Openshift_Api(Api):
    api_version = 'oapi/v1'

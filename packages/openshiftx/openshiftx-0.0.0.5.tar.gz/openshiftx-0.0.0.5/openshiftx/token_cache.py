# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     local_cache
   Description :
   Author :       潘晓华
   date：          2018/7/2
-------------------------------------------------
"""

import time
import json
class TokenCache(object):
    def __init__(self, cache_file):
        self.cache_file = cache_file
        self.token = None

    def get(self):
        if not self.token:
            try:
                with open(self.cache_file, 'r') as f:
                    data = f.readline()
            except Exception as e:
                return None
            data = eval(data)
            expire_time = data['expire']
            if int(time.time()) > int(expire_time):
                self.data = None
                return None
            self.token = data['token']
            return data['token']
        else:
            return self.token

    def set(self, token, expire):
        self.token = token
        data = "{'token': '%s', 'expire':'%s'}" % (token,expire)
        with open(self.cache_file, 'w') as f:
            f.write(data)


token_cache = TokenCache('./.token')
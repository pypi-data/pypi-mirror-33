# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     pod
   Description :
   Author :       潘晓华
   date：          2018/7/3
-------------------------------------------------
"""

from .api import K8s_Api

class Pod(K8s_Api):

    @classmethod
    def get_all(cls, project=None, params={}):
        if None == project:
            pod_data = cls.get('pods', params=params)
        else:
            pod_data = cls.get('namespaces/%s/pods' % project, params=params)

        return pod_data

    @classmethod
    def get_pod_by_selector(cls, project, selector):
        pod_data = cls.get('namespaces/%s/pods' % project, params={"labelSelector":selector})
        return pod_data

    @classmethod
    def get_ready_pods_by_selector(cls, project, selector):
        pods = cls.get_pod_by_selector(project=project, selector=selector)
        return [item for item in pods['items'] if  len(item['status']['conditions']) == 3 and item['status']['conditions'][1]['status'] == 'True']

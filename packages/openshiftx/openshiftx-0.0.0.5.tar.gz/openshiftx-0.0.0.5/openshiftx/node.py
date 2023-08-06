# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     node
   Description :
   Author :       潘晓华
   date：          2018/7/3
-------------------------------------------------
"""

from .api import K8s_Api

class Node(K8s_Api):
    @classmethod
    def get_all(cls):
        result = cls.get('nodes')

        return result

    @classmethod
    def get_all_names(cls):
        names = []
        nodes_info = cls.get_all()
        if 'items' not in  nodes_info.keys():
            print nodes_info
        for node in nodes_info['items']:
            names.append(node['metadata']['name'])
        return names

    @classmethod
    def get_info_by_node(cls, node_name):
        data = cls.get('nodes/%s' % node_name)
        return data

if __name__ == '__main__':
    pass
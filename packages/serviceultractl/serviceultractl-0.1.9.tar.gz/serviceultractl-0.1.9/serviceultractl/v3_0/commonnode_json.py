# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .base.commonnode import CommonNode as Node_base


class CommonNode(object):
    @staticmethod
    def list(auth):
        try:
            data = Node_base._list(auth)
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node_info = dict(id=node.get("id", ""),
                                 name=node.get("name", ""),
                                 occupied=node.get("occupied", ""),
                                 ip=node.get("ip", ""),
                                 administration_ip=node.get("administration_ip"),
                                 username=node.get("username", ""),
                                 ssh_port=node.get("ssh_port", ""),
                                 cluster_id=node.get("cluster_id", ""),
                                 cluster_name=node.get("cluster_name", ""),
                                 data_dirs=node.get("data_dirs", []),
                                 create_time=node.get("create_time", "")
                                 )
                nodes_info.append(node_info)
            # print json.dumps(nodes_info)
            print json.dumps(dict(nodes=nodes_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, machineid):
        try:
            data = Node_base._show(auth, machineid)
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node_info = dict(id=node.get("id", ""),
                                 name=node.get("name", ""),
                                 occupied=node.get("occupied", ""),
                                 ip=node.get("ip", ""),
                                 administration_ip=node.get("administration_ip", ""),
                                 username=node.get("username", ""),
                                 ssh_port=node.get("ssh_port", ""),
                                 cluster_id=node.get("cluster_id", ""),
                                 cluster_name=node.get("cluster_name", ""),
                                 data_dirs=node.get("data_dirs", ""),
                                 create_time=node.get("create_time", "")
                                 )
                nodes_info.append(node_info)
            print json.dumps(nodes_info[0] if len(nodes_info) > 0 else dict(), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def list_by_clusterid(auth, clusterid):
        try:
            data1, data2 = Node_base._list_by_clusterid(auth, clusterid)
            usages = {}
            for _k, _v in data2.items():
                if not isinstance(_v, list):
                    continue
                for v in _v:
                    usages.setdefault(v.get("node_id", ""), {}).setdefault(_k, v.get("value", 0))
                    # usages[v.get("node_id", "")][_k] = v.get("value", 0)
            nodes_info = []
            nodes = data1.get("nodes", [])
            for node in nodes:
                node.update(usages.get(node.get("id", ""), {}))
                node_info = dict(id=node.get("id", ""),
                                 name=node.get("name", ""),
                                 lifecycle=node.get("lifecycle", ""),
                                 status_summary=node.get("status_summary", ""),
                                 running_status=node.get("running_status", ""),
                                 ip=node.get("ip", ""),
                                 administration_ip=node.get("administration_ip", ""),
                                 username=node.get("username", ""),
                                 ssh_port=node.get("ssh_port", ""),
                                 cluster_id=node.get("cluster_id", ""),
                                 cluster_name=node.get("cluster_name", ""),
                                 data_dirs=node.get("data_dirs", ""),
                                 cpu_usages=node.get("cpu_usages", ""),
                                 disk_usages=node.get("disk_usages", ""),
                                 memory_usages=node.get("memory_usages", ""),
                                 create_time=node.get("create_time", "")
                                 )
                nodes_info.append(node_info)
            print json.dumps(dict(nodes=nodes_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        try:
            data = Node_base._statistics(auth)
            node = data.get("common_nodes", {})
            node.update(data.get("resources", {}))
            node_info = dict(total=node.get("total", ""),
                             occupied=node.get("occupied", ""),
                             disk=node.get("disk", ""),
                             memory=node.get("memory", ""),
                             cpu=node.get("cpu", "")
                             )
            print json.dumps(node_info, indent=4, ensure_ascii=False)
        except Exception as e:
            raise

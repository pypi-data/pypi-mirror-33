# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from ..utils.common_utils import obj_replace_time_field
from .base.cluster import Cluster as Cluster_base


class Cluster(object):
    @staticmethod
    def list(auth):
        try:
            data = Cluster_base._list(auth)
            clusters_info = []
            clusters = data.get("clusters", [])
            users = data.get("users", {})
            for cluster in clusters:
                cluster_info = dict(
                    id=cluster.get("id", ""),
                    name=cluster.get("name", ""),
                    lifecycle_conf=cluster.get("lifecycle_conf", ""),
                    status_summary=cluster.get("status_summary", ""),
                    running_status=cluster.get("running_status", ""),
                    cluster_name=users.get(cluster.get("creater", ""), {}).get("nickname", "")
                                 or users.get(cluster.get("creater", ""), {}).get("username", ""),
                    create_time=cluster.get("create_time", "")
                )
                clusters_info.append(cluster_info)
            print json.dumps(dict(clusters=clusters_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, clusterid):
        try:
            data = Cluster_base._show(auth, clusterid)
            cluster_info = {}
            cluster = data
            cluster_info["id"] = cluster.get("id", "")
            cluster_info["name"] = cluster.get("name", "")
            cluster_info["lifecycle"] = cluster.get("lifecycle", "")
            cluster_info["status_summary"] = cluster.get("status_summary", "")
            cluster_info["running_status"] = cluster.get("running_status", "")
            cluster_info["create_time"] = cluster.get("create_time", "")
            print json.dumps(cluster_info, indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def statistics_by_id(auth, clusterid):
        try:
            data1, data2 = Cluster_base._statistics_by_id(auth, clusterid)
            cluster = data1[0] if len(data1) > 0 else {}
            if cluster:
                cluster["monitor"] = data2
            print json.dumps(cluster, indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        try:
            data = Cluster_base._statistics(auth)
            print json.dumps(data, indent=4, ensure_ascii=False)
        except Exception as e:
            raise
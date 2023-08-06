# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.cluster import Cluster as Cluster_base


lifecycle_conf_en = {"running": "RUNNING",
                  "setting": "SETTING",
                  "executing": "EXECUTING"}
status_summary_conf_en = {
    "setting": "SETTING",
    "successfully_deployed": "SUCCESSFULLY DEPLOYED",
    "failed_deployed": "FAILED DEPLOYED",
    "executing": "EXECUTING"
}
running_status_conf_en = {
    "green": "Normal",
    "yellow": "Warning",
    "red": "Error"
}


class Cluster(object):
    @staticmethod
    def list(auth):
        try:
            data = Cluster_base._list(auth)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Cluster Name"
            header["status_summary_running"] = "Status"
            header["application_num"] = "Application Num"
            header["creater_name"] = "Creator"
            header["create_time"] = "Create Time"
            clusters_info = []
            clusters = data.get("clusters", [])
            users = data.get("users", {})
            for cluster in clusters:
                cluster = obj_replace_time_field(cluster, ["create_time"])
                cluster["status_summary_running"] = status_format(cluster.get("lifecycle", ""), lifecycle_conf_en,
                                                                  cluster.get("status_summary", ""),
                                                                  status_summary_conf_en,
                                                                  cluster.get("running_status", ""),
                                                                  running_status_conf_en)
                cluster["creater_name"] = users.get(cluster.get("creater", ""), {}).get("nickname", "") \
                                          or users.get(cluster.get("creater", ""), {}).get("username", "")
                cluster_info = [cluster.get(key, "") for key in header]
                clusters_info.append(cluster_info)
            print_table(header.values(), clusters_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, clusterid):
        try:
            data = Cluster_base._show(auth, clusterid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Cluster Name"
            header["status_summary_running"] = "Status"
            header["create_time"] = "Create Time"
            clusters_info = []
            cluster = data
            cluster = obj_replace_time_field(cluster, ["create_time"])
            cluster["status_summary_running"] = status_format(cluster.get("lifecycle", ""), lifecycle_conf_en,
                                                              cluster.get("status_summary", ""), status_summary_conf_en,
                                                              cluster.get("running_status", ""), running_status_conf_en)
            cluster_info = [cluster.get(key, "") for key in header]
            clusters_info.append(cluster_info)
            print_table(header.values(), clusters_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def statistics_by_id(auth, clusterid):
        try:
            data1, data2 = Cluster_base._statistics_by_id(auth, clusterid)
            header = collections.OrderedDict()
            header["cluster_id"] = "ID"
            header["cluster_name"] = "Cluster name"
            header["total"] = "Total Node"
            header["running"] = "Running Node"
            header["executing"] = "Executing Node"
            header["setting"] = "Setting Node"
            header["cpu_total"] = "Total CPU"
            header["cpu_used"] = "Used CPU"
            header["cpu_usage"] = "CPU Usage(%)"
            header["disk_total"] = "Total Disk(G)"
            header["disk_used"] = "Used Disk"
            header["disk_usage"] = "Disk Usage(%)"
            header["memory_total"] = "Total Memory(M)"
            header["memory_used"] = "Used Memory"
            header["memory_usage"] = "Memory Usage(%)"
            clusters_info = []
            clusters = data1
            for cluster in clusters:
                nodes = cluster.get("nodes", {})
                resources = cluster.get("resources", {})
                cluster.update(nodes)
                cluster.update(resources)
                cluster.update(data2)
                cluster["cpu_used"] = int(cluster.get("cpu_used", 0))
                cluster["cpu_total"] = int(cluster.get("cpu_total", 0))
                cluster_info = [cluster.get(key, "") for key in header]
                clusters_info.append(cluster_info)
            print_table(header.values(), clusters_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        try:
            data = Cluster_base._statistics(auth)
            print "Application Status"
            header1 = collections.OrderedDict()
            header1["error"] = "Error"
            header1["running"] = "Running"
            header1["setting"] = "Setting"
            header1["executing"] = "Executing"
            header1["total"] = "Total"
            counts_info = []
            count = data.get("count", {})
            count_info = [count.get(key, "") for key in header1]
            counts_info.append(count_info)
            print_table(header1.values(), counts_info, auth.encoding)
            print "CPU usages(cor)："
            header2 = collections.OrderedDict()
            header2["cluster_id"] = "Cluster id"
            header2["cluster_name"] = "Cluster name"
            header2["cpu_used"] = "Used CPU"
            header2["cpu_total"] = "Total CPU"
            cpus_info = []
            cpus = data.get("ranks", {}).get("cpu", [])
            for cpu in cpus:
                cpu["cpu_used"] = int(cpu.get("cpu_used", 0))
                cpu["cpu_total"] = int(cpu.get("cpu_total", 0))
                cpu_info = [cpu.get(key, "") for key in header2]
                cpus_info.append(cpu_info)
            print_table(header2.values(), cpus_info, auth.encoding)
            print "Memory usages(M)："
            header3 = collections.OrderedDict()
            header3["cluster_id"] = "Cluster id"
            header3["cluster_name"] = "Cluster name"
            header3["memory_used"] = "Used memory"
            header3["memory_total"] = "Total memory"
            memorys_info = []
            memorys = data.get("ranks", {}).get("memory", [])
            for memory in memorys:
                memory_info = [memory.get(key, "") for key in header3]
                memorys_info.append(memory_info)
            print_table(header3.values(), memorys_info, auth.encoding)
        except Exception as e:
            raise

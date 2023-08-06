# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.cluster import Cluster as Cluster_base


lifecycle_conf_ch = {"running": u"已上线",
                  "setting": u"配置中",
                  "executing": u"执行中"}
status_summary_conf_ch = {
    "setting": u"配置中",
    "successfully_deployed": u"已上线",
    "failed_deployed": u"上线失败",
    "executing": u"执行中"
}
running_status_conf_ch = {
    "green": u"正常",
    "yellow": u"异常",
    "red": u"错误"
}


class Cluster(object):
    @staticmethod
    def list(auth):
        try:
            data = Cluster_base._list(auth)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"集群名称"
            header["status_summary_running"] = u"当前状态"
            header["application_num"] = u"应用数"
            header["creater"] = u"创建人"
            header["create_time"] = u"创建时间"
            clusters_info = []
            clusters = data.get("clusters", [])
            users = data.get("users", {})
            for cluster in clusters:
                cluster = obj_replace_time_field(cluster, ["create_time"])
                cluster["status_summary_running"] = status_format(cluster.get("lifecycle", ""), lifecycle_conf_ch,
                                                                  cluster.get("status_summary", ""),
                                                                  status_summary_conf_ch,
                                                                  cluster.get("running_status", ""),
                                                                  running_status_conf_ch)
                cluster_info = [cluster.get(key, "") for key in header]
                creater_name = users.get(cluster.get("creater", ""), {}).get("nickname", "") \
                               or users.get(cluster.get("creater", ""), {}).get("username", "")
                cluster_info[header.keys().index("creater")] = creater_name
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
            header["name"] = u"集群名称"
            header["status_summary_running"] = u"当前状态"
            header["create_time"] = u"创建时间"
            clusters_info = []
            cluster = data
            cluster = obj_replace_time_field(cluster, ["create_time"])
            cluster["status_summary_running"] = status_format(cluster.get("lifecycle", ""), lifecycle_conf_ch,
                                                              cluster.get("status_summary", ""), status_summary_conf_ch,
                                                              cluster.get("running_status", ""), running_status_conf_ch)
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
            header["cluster_name"] = u"集群名称"
            header["total"] = u"主机总数（个）"
            header["running"] = u"已上线"
            header["executing"] = u"上线中"
            header["setting"] = u"配置中"
            header["cpu_total"] = u"CPU总数（个）"
            header["cpu_used"] = u"CPU已使用"
            header["cpu_usage"] = u"CPU使用率（%）"
            header["disk_total"] = u"磁盘总数（G）"
            header["disk_used"] = u"磁盘已使用"
            header["disk_usage"] = u"磁盘使用率（%）"
            header["memory_total"] = u"内存总数（M）"
            header["memory_used"] = u"内存已使用"
            header["memory_usage"] = u"内存使用率（%）"
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
            print u"应用状态："
            header1 = collections.OrderedDict()
            header1["error"] = u"异常"
            header1["running"] = u"运行中"
            header1["setting"] = u"配置中"
            header1["executing"] = u"执行中"
            header1["total"] = u"总数"
            counts_info = []
            count = data.get("count", {})
            count_info = [count.get(key, "") for key in header1]
            counts_info.append(count_info)
            print_table(header1.values(), counts_info, auth.encoding)
            print u"各集群CPU使用情况(核)："
            header2 = collections.OrderedDict()
            header2["cluster_id"] = u"ID"
            header2["cluster_name"] = u"集群名称"
            header2["cpu_used"] = u"CPU已使用"
            header2["cpu_total"] = u"CPU总数"
            cpus_info = []
            cpus = data.get("ranks", {}).get("cpu", [])
            for cpu in cpus:
                cpu["cpu_used"] = int(cpu.get("cpu_used", 0))
                cpu["cpu_total"] = int(cpu.get("cpu_total", 0))
                cpu_info = [cpu.get(key, "") for key in header2]
                cpus_info.append(cpu_info)
            print_table(header2.values(), cpus_info, auth.encoding)
            print u"各集群内存使用情况(M)："
            header3 = collections.OrderedDict()
            header3["cluster_id"] = u"ID"
            header3["cluster_name"] = u"集群名称"
            header3["memory_used"] = u"内存已使用"
            header3["memory_total"] = u"内存总数"
            memorys_info = []
            memorys = data.get("ranks", {}).get("memory", [])
            for memory in memorys:
                memory_info = [memory.get(key, "") for key in header3]
                memorys_info.append(memory_info)
            print_table(header3.values(), memorys_info, auth.encoding)
        except Exception as e:
            raise
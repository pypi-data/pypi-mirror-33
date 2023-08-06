# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.commonnode import CommonNode as Node_base


occupied_conf_ch = {True: u"已用",
                 False: u"可用"}
lifecycle_conf_ch = {"running": u"已上线",
                  "setting": u"配置中",
                  "executing": u"执行中"}
status_summary_conf_ch = {"successfully_deployed": u"已上线",
                       "failed_deployed": u"上线失败",
                       "executing": u"执行中",
                       "setting": u"配置中"}
running_status_conf_ch = {"green": u"正常",
                       "gray": u"",
                       "yellow": u"异常",
                       "red": u"错误"}


class CommonNode(object):
    @staticmethod
    def list(auth):
        try:
            data = Node_base._list(auth)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"主机名"
            header["occupied"] = u"当前状态"
            header["ip"] = u"服务IP"
            header["administration_ip"] = u"管理IP"
            header["username"] = u"用户名"
            header["ssh_port"] = u"端口"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名称"
            header["data_dirs_new"] = u"数据目录"
            header["create_time"] = u"创建时间"
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                node["occupied"] = occupied_conf_ch.get(node.get("occupied", None), u"")
                data_dirs = node.get("data_dirs", [])
                node["data_dirs_new"] = "\n".join(
                    ["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs])
                node_info = [node.get(key, "") for key in header]
                nodes_info.append(node_info)
            # for node_info in nodes_info:
            #     data_dirs_tmp = node_info[header.keys().index("data_dirs")]
            #     # format
            #     # [{ "path": "/data","default": true,"name": "normal"},
            #     #  {"path": "/ssd","default": false,"name": "ssh"}]
            #     # to
            #     # "normal:/data\nssh:/ssd"
            #     data_dirs = "\n".join(["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs_tmp])
            #     node_info[header.keys().index("data_dirs")] = data_dirs
            print_table(header.values(), nodes_info, auth.encoding)
        except Exception as e:
            raise Exception("Failed")

    @staticmethod
    def show(auth, machineid):
        try:
            data = Node_base._show(auth, machineid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"主机名"
            header["occupied"] = u"当前状态"
            header["ip"] = u"服务IP"
            header["administration_ip"] = u"管理IP"
            header["username"] = u"用户名"
            header["ssh_port"] = u"端口"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名称"
            header["data_dirs_new"] = u"数据目录"
            header["create_time"] = u"创建时间"
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                node["occupied"] = occupied_conf_ch.get(node.get("occupied", None), u"")
                data_dirs = node.get("data_dirs", [])
                node["data_dirs_new"] = "\n".join(
                    ["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs])
                node_info = [node.get(key, "") for key in header]
                nodes_info.append(node_info)
            # for node_info in nodes_info:
            #     data_dirs_tmp = node_info[header.keys().index("data_dirs")]
            #     # format
            #     # [{ "path": "/data","default": true,"name": "normal"},
            #     #  {"path": "/ssd","default": false,"name": "ssh"}]
            #     # to
            #     # "normal:/data\nssh:/ssd"
            #     data_dirs = "\n".join(
            #         ["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs_tmp])
            #     node_info[header.keys().index("data_dirs")] = data_dirs
            print_table(header.values(), nodes_info, auth.encoding)
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
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"主机名"
            header["status_summary_running"] = u"当前状态"
            header["ip"] = u"服务IP"
            header["administration_ip"] = u"管理IP"
            header["username"] = u"用户名"
            header["ssh_port"] = u"端口"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名称"
            header["data_dirs_new"] = u"数据目录"
            header["cpu_usages"] = u"CPU使用率（%）"
            header["disk_usages"] = u"磁盘使用率（%）"
            header["memory_usages"] = u"内存使用率（%）"
            header["create_time"] = u"创建时间"
            nodes_info = []
            nodes = data1.get("nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                status_summary_running = status_format(node.get("lifecycle", ""), lifecycle_conf_ch,
                                                       node.get("status_summary", ""), status_summary_conf_ch,
                                                       node.get("running_status", ""), running_status_conf_ch)
                node["status_summary_running"] = status_summary_running
                node.update(usages.get(node.get("id", ""), {}))
                data_dirs = node.get("data_dirs", [])
                node["data_dirs_new"] = "\n".join(
                    ["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs])
                node_info = [node.get(key, "") for key in header]
                nodes_info.append(node_info)
            # for node_info in nodes_info:
            #     data_dirs_tmp = node_info[header.keys().index("data_dirs")]
            #     # format
            #     # [{ "path": "/data","default": true,"name": "normal"},
            #     #  {"path": "/ssd","default": false,"name": "ssh"}]
            #     # to
            #     # "normal:/data\nssh:/ssd"
            #     data_dirs = "\n".join(
            #         ["{}:{}".format(data_dir["name"], data_dir["path"]) for data_dir in data_dirs_tmp])
            #     node_info[header.keys().index("data_dirs")] = data_dirs
            print_table(header.values(), nodes_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        try:
            data = Node_base._statistics(auth)
            header = collections.OrderedDict()
            header["total"] = u"主机总数"
            header["occupied"] = u"已用"
            header["disk"] = u"磁盘总量(G)"
            header["memory"] = u"内存总量(M)"
            header["cpu"] = u"CPU总量(核)"
            nodes_info = []
            nodes = data.get("common_nodes", {})
            nodes.update(data.get("resources", {}))
            node_info = [nodes.get(key, "") for key in header]
            nodes_info.append(node_info)
            print_table(header.values(), nodes_info, auth.encoding)
        except Exception as e:
            raise












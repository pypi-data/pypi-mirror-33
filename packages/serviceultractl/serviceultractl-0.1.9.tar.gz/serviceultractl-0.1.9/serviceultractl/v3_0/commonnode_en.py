# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.commonnode import CommonNode as Node_base


occupied_conf_en = {True: "Occupied",
                    False: "Idle"}
lifecycle_conf_en = {"running": "Running",
                  "setting": "Setting",
                  "executing": "Executing"}
status_summary_conf_en = {"successfully_deployed": "Successfully deployed",
                       "failed_deployed": "Failed deployed",
                       "executing": "Executing",
                       "setting": "Setting"}
running_status_conf_en = {"green": "Normal",
                       "gray": "",
                       "yellow": "Warning",
                       "red": "Error"}


class CommonNode(object):
    @staticmethod
    def list(auth):
        try:
            data = Node_base._list(auth)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Hostname"
            header["occupied"] = "Occupied"
            header["ip"] = "Service IP"
            header["administration_ip"] = "Administration IP"
            header["username"] = "Username"
            header["ssh_port"] = "Ssh Port"
            header["cluster_id"] = "Cluster ID"
            header["cluster_name"] = "Cluster Name"
            header["data_dirs_new"] = "Data Dirs"
            header["create_time"] = "Create Time"
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                node["occupied"] = occupied_conf_en.get(node.get("occupied", None), "")
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
    def show(auth, machineid):
        try:
            data = Node_base._show(auth, machineid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Hostname"
            header["occupied"] = "Occupied"
            header["ip"] = "Service IP"
            header["administration_ip"] = "Administration IP"
            header["username"] = "Username"
            header["ssh_port"] = "Ssh Port"
            header["cluster_id"] = "Cluster ID"
            header["cluster_name"] = "Cluster Name"
            header["data_dirs_new"] = "Data Dirs"
            header["create_time"] = "Create Time"
            nodes_info = []
            nodes = data.get("common_nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                node["occupied"] = occupied_conf_en.get(node.get("occupied", None), u"")
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
            header["name"] = "Hostname"
            header["status_summary_running"] = "Status"
            header["ip"] = "Service IP"
            header["administration_ip"] = "Administration IP"
            header["username"] = "Username"
            header["ssh_port"] = "Ssh Port"
            header["cluster_id"] = "Cluster ID"
            header["cluster_name"] = "Cluster Name"
            header["data_dirs_new"] = "Data Dirs"
            header["cpu_usages"] = "CPU Usages（%）"
            header["disk_usages"] = "Disk Usages（%）"
            header["memory_usages"] = "Memory Usages（%）"
            header["create_time"] = "Create Time"
            nodes_info = []
            nodes = data1.get("nodes", [])
            for node in nodes:
                node = obj_replace_time_field(node, ["create_time"])
                status_summary_running = status_format(node.get("lifecycle", ""), lifecycle_conf_en,
                                                       node.get("status_summary", ""), status_summary_conf_en,
                                                       node.get("running_status", ""), running_status_conf_en)
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
            header["total"] = "Total host num"
            header["occupied"] = "Occupied num"
            header["disk"] = "Total Disk(G)"
            header["memory"] = "Total Memory(M)"
            header["cpu"] = "Total CPU(Cors)"
            nodes_info = []
            nodes = data.get("common_nodes", {})
            nodes.update(data.get("resources", {}))
            node_info = [nodes.get(key, "") for key in header]
            nodes_info.append(node_info)
            print_table(header.values(), nodes_info, auth.encoding)
        except Exception as e:
            raise

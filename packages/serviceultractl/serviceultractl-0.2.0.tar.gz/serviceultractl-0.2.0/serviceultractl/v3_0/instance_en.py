# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.instance import Instance as Ins_base


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


class Instance(object):
    @staticmethod
    def list(auth, serviceid):
        try:
            data = Ins_base._list(auth, serviceid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Name"
            header["status_summary_running"] = "Status"
            header["micro_service_id"] = "Microservice ID"
            header["service_id"] = "Service ID"
            header["application_id"] = "Application ID"
            header["cluster_id"] = "Cluster ID"
            header["node_id"] = "Node ID"
            header["node_name"] = "Node Name"
            header["data_path_instance"] = "Data Dir"
            header["create_time"] = "Create Time"
            instances_info = []
            microservices = data.get("micro_services", [])
            for microservice in microservices:
                for instance in microservice.get("instances", []):
                    instance["node_id"] = instance.get("node_id") or instance.get("running_node_id")
                    instance["node_name"] = instance.get("node_name") or instance.get("running_node_name")
                    status_summary_running = status_format(instance.get("lifecycle", ""), lifecycle_conf_en,
                                                           instance.get("status_summary", ""), status_summary_conf_en,
                                                           instance.get("running_status", ""), running_status_conf_en)
                    instance["status_summary_running"] = status_summary_running
                    instance = obj_replace_time_field(instance, ["create_time"])
                    instance_info = [instance.get(key, "") for key in header]
                    instances_info.append(instance_info)
            print_table(header.values(), instances_info, auth.encoding)
        except Exception as e:
            raise

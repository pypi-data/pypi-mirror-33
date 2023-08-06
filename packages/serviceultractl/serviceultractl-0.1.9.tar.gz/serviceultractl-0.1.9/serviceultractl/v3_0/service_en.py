# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.service import Service as Srv_base


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


class Service(object):
    @staticmethod
    def list(auth, appid):
        try:
            data = Srv_base._list(auth, appid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Name"
            header["status_summary_running"] = "Status"
            header["application_id"] = "Application ID"
            header["cluster_id"] = "Cluster ID"
            header["cluster_name"] = "Cluster Name"
            header["prototype"] = "Prototype"
            header["version"] = "Version"
            header["micro_service_num"] = "Micro Service Num"
            header["cpu_allocated_total"] = "Used CPU(cor)"
            header["memory_allocated_total"] = "Used Memory(M)"
            header["create_time"] = "Create Time"
            services_info = []
            services = data.get("services", [])
            for service in services:
                service["cpu_allocated_total"] = "{}/{}".format(
                    service.get("resource_info", {}).get("cpu_allocated", "NaN"),
                    service.get("resource_info", {}).get("cpu_total", "NaN"))
                service["memory_allocated_total"] = "{}/{}".format(
                    service.get("resource_info", {}).get("memory_allocated", "NaN"),
                    service.get("resource_info", {}).get("memory_total", "NaN"))
                service = obj_replace_time_field(service, ["create_time"])
                status_summary_running = status_format(service.get("lifecycle", ""), lifecycle_conf_en,
                                                       service.get("status_summary", ""), status_summary_conf_en,
                                                       service.get("running_status", ""), running_status_conf_en)
                service["status_summary_running"] = status_summary_running
                service_info = [service.get(key, "") for key in header]
                services_info.append(service_info)
            print_table(header.values(), services_info, auth.encoding)
        except Exception as e:
            raise

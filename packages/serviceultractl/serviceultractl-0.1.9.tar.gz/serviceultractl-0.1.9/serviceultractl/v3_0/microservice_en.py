# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.microservice import MicroService as Ms_base


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


class MicroService(object):
    @staticmethod
    def list(auth, serviceid):
        try:
            data = Ms_base._list(auth, serviceid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Microservice Name"
            header["status_summary_running"] = "Status"
            header["service_id"] = "Service ID"
            header["application_id"] = "Application ID"
            header["cluster_id"] = "Cluster ID"
            header["prototype"] = "Service Type"
            header["instance_num"] = "Instance Num"
            header["version"] = "Version"
            header["cpu"] = "CPU(cor)"
            header["memory"] = "Memory(M)"
            header["create_time"] = "Create Time"
            microservices_info = []
            microservices = data.get("micro_services", [])
            for microservice in microservices:
                microservice = obj_replace_time_field(microservice, ["create_time"])
                status_summary_running = status_format(microservice.get("lifecycle", ""), lifecycle_conf_en,
                                                       microservice.get("status_summary", ""), status_summary_conf_en,
                                                       microservice.get("running_status", ""), running_status_conf_en)
                microservice["status_summary_running"] = status_summary_running
                microservice_info = [microservice.get(key, "") for key in header]
                microservices_info.append(microservice_info)
            print_table(header.values(), microservices_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth, serviceid):
        try:
            data = Ms_base._statistics(auth, serviceid)
            header = collections.OrderedDict()
            header["cpu"] = "CPU(cor)"
            header["instance_num"] = "Instance Num"
            header["memory"] = "Memory(M)"
            header["micro_service_num"] = "Micro Service Num"
            statistics_infos = []
            statistics = data.get("statistics", {})
            statistics_info = [statistics.get(key, "") for key in header]
            statistics_infos.append(statistics_info)
            print_table(header.values(), statistics_infos, auth.encoding)
        except Exception as e:
            raise

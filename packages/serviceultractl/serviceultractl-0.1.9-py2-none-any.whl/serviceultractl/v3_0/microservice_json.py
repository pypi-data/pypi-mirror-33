# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import collections
from .base.microservice import MicroService as Ms_base


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
                microservice_info = dict(id=microservice.get("id", ""),
                                         name=microservice.get("name", ""),
                                         lifecycle=microservice.get("lifecycle", ""),
                                         status_summary=microservice.get("status_summary", ""),
                                         running_status=microservice.get("running_status", ""),
                                         service_id=microservice.get("service_id", ""),
                                         application_id=microservice.get("application_id", ""),
                                         cluster_id=microservice.get("cluster_id", ""),
                                         prototype=microservice.get("prototype", ""),
                                         instance_num=microservice.get("instance_num", ""),
                                         version=microservice.get("version", ""),
                                         cpu=microservice.get("cpu", ""),
                                         memory=microservice.get("memory", ""),
                                         create_time=microservice.get("create_time", ""),
                                         )
                microservices_info.append(microservice_info)
            print json.dumps(dict(micro_services=microservices_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth, serviceid):
        try:
            data = Ms_base._statistics(auth, serviceid)
            statistics = data.get("statistics", {})
            print json.dumps(statistics, indent=4, ensure_ascii=False)
        except Exception as e:
            raise

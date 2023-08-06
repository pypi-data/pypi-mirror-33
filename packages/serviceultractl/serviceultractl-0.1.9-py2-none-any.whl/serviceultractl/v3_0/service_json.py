# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .base.service import Service as Srv_base


class Service(object):
    @staticmethod
    def list(auth, appid):
        try:
            data = Srv_base._list(auth, appid)
            services_info = []
            services = data.get("services", [])
            for service in services:
                service_info = dict(id=service.get("id", ""),
                                    name=service.get("name", ""),
                                    lifecycle=service.get("lifecycle", ""),
                                    status_summary=service.get("status_summary", ""),
                                    running_status=service.get("running_status", ""),
                                    application_id=service.get("application_id", ""),
                                    cluster_id=service.get("cluster_id", ""),
                                    cluster_name=service.get("cluster_name", ""),
                                    prototype=service.get("prototype", ""),
                                    version=service.get("version", ""),
                                    micro_service_num=service.get("micro_service_num", ""),
                                    cpu_allocated_total=service.get("cpu_allocated_total", ""),
                                    memory_allocated_total=service.get("memory_allocated_total", ""),
                                    create_time=service.get("create_time", ""),
                                    )
                services_info.append(service_info)
            print json.dumps(dict(services=services_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .base.instance import Instance as Ins_base


class Instance(object):
    @staticmethod
    def list(auth, serviceid):
        try:
            data = Ins_base._list(auth, serviceid)
            instances_info = []
            microservices = data.get("micro_services", [])
            for microservice in microservices:
                for instance in microservice.get("instances", []):
                    instance_info = dict(id=instance.get("id", ""),
                                         name=instance.get("name", ""),
                                         lifecycle=instance.get("lifecycle", ""),
                                         status_summary=instance.get("status_summary", ""),
                                         running_status=instance.get("running_status", ""),
                                         micro_service_id=instance.get("name", ""),
                                         service_id=instance.get("service_id", ""),
                                         application_id=instance.get("application_id", ""),
                                         cluster_id=instance.get("cluster_id", ""),
                                         node_id=instance.get("node_id", ""),
                                         running_node_id=instance.get("running_node_id", ""),
                                         node_name=instance.get("node_name", ""),
                                         running_node_name=instance.get("running_node_name", ""),
                                         data_path_instance=instance.get("data_path_instance", ""),
                                         create_time=instance.get("create_time", ""),
                                         )
                    instances_info.append(instance_info)
            print json.dumps(dict(instances=instances_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

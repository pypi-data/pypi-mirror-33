# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.instance import Instance as Ins_base


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


class Instance(object):
    @staticmethod
    def list(auth, serviceid):
        try:
            data = Ins_base._list(auth, serviceid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"实例名"
            header["status_summary_running"] = u"当前状态"
            header["micro_service_id"] = u"微服务ID"
            header["service_id"] = u"服务ID"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["node_id"] = u"主机ID"
            header["node_name"] = u"主机名"
            header["data_path_instance"] = u"数据目录"
            header["create_time"] = u"创建时间"
            instances_info = []
            microservices = data.get("micro_services", [])
            for microservice in microservices:
                for instance in microservice.get("instances", []):
                    instance["node_id"] = instance.get("node_id") or instance.get("running_node_id")
                    instance["node_name"] = instance.get("node_name") or instance.get("running_node_name")
                    status_summary_running = status_format(instance.get("lifecycle", ""), lifecycle_conf_ch,
                                                           instance.get("status_summary", ""), status_summary_conf_ch,
                                                           instance.get("running_status", ""), running_status_conf_ch)
                    instance["status_summary_running"] = status_summary_running
                    instance = obj_replace_time_field(instance, ["create_time"])
                    instance_info = [instance.get(key, "") for key in header]
                    instances_info.append(instance_info)
            print_table(header.values(), instances_info, auth.encoding)
        except Exception as e:
            raise

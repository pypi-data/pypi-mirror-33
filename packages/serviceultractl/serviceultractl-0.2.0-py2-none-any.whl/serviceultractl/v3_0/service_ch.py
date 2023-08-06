# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.service import Service as Srv_base


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


class Service(object):
    @staticmethod
    def list(auth, appid):
        try:
            data = Srv_base._list(auth, appid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"服务名"
            header["status_summary_running"] = u"当前状态"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名"
            header["prototype"] = u"类型"
            header["version"] = u"版本"
            header["micro_service_num"] = u"微服务数"
            header["cpu_allocated_total"] = u"CPU使用率（核）"
            header["memory_allocated_total"] = u"内存使用率（M）"
            header["create_time"] = u"创建时间"
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
                status_summary_running = status_format(service.get("lifecycle", ""), lifecycle_conf_ch,
                                                       service.get("status_summary", ""), status_summary_conf_ch,
                                                       service.get("running_status", ""), running_status_conf_ch)
                service["status_summary_running"] = status_summary_running
                service_info = [service.get(key, "") for key in header]
                services_info.append(service_info)
            print_table(header.values(), services_info, auth.encoding)
        except Exception as e:
            raise

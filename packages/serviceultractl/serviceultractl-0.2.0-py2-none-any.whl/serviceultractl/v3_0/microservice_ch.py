# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.microservice import MicroService as Ms_base


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


class MicroService(object):
    @staticmethod
    def list(auth, serviceid):
        try:
            data = Ms_base._list(auth, serviceid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"微服务名"
            header["status_summary_running"] = u"当前状态"
            header["service_id"] = u"服务ID"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["prototype"] = u"服务类型"
            header["instance_num"] = u"实例数"
            header["version"] = u"版本"
            header["cpu"] = u"CPU（核）"
            header["memory"] = u"内存（M）"
            header["create_time"] = u"创建时间"
            microservices_info = []
            microservices = data.get("micro_services", [])
            for microservice in microservices:
                microservice = obj_replace_time_field(microservice, ["create_time"])
                status_summary_running = status_format(microservice.get("lifecycle", ""), lifecycle_conf_ch,
                                                       microservice.get("status_summary", ""), status_summary_conf_ch,
                                                       microservice.get("running_status", ""), running_status_conf_ch)
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
            header["cpu"] = u"CPU（核）"
            header["instance_num"] = u"实例个数"
            header["memory"] = u"内存（M）"
            header["micro_service_num"] = u"微服务数"
            statistics_infos = []
            statistics = data.get("statistics", {})
            statistics_info = [statistics.get(key, "") for key in header]
            statistics_infos.append(statistics_info)
            print_table(header.values(), statistics_infos, auth.encoding)
        except Exception as e:
            raise

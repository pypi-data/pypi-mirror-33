# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.task import Task as Task_base


lifecycle_conf_ch = {"scheduling": u"调度中",
                     "setting": u"配置中"}
running_status_conf_ch = {"idle": u"未运行",
                          "running": u"运行中",
                          "success": u"正常",
                          "failed": u"失败",
                          "killed": u"中止"}


class Task(object):
    @staticmethod
    def list(auth, appid):
        try:
            data = Task_base._list(auth, appid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = u"任务名"
            header["status_summary_running"] = u"当前状态"
            header["application_id"] = u"应用ID"
            header["cluster_id"] = u"集群ID"
            header["cluster_name"] = u"集群名"
            header["version"] = u"版本"
            header["prototype"] = u"类型"
            header["cpu_allocated_total"] = u"CPU使用率（核）"
            header["memory_allocated_total"] = u"内存使用率（M）"
            header["schedule_start"] = u"任务开始时间"
            header["schedule_interval"] = u"任务间隔时间"
            header["create_time"] = u"创建时间"
            tasks_info = []
            tasks = data.get("tasks", [])
            for task in tasks:
                task["cpu_allocated_total"] = "{}/{}".format(
                    task.get("resource_info", {}).get("cpu_allocated", "NaN"),
                    task.get("resource_info", {}).get("cpu_total", "NaN"))
                task["memory_allocated_total"] = "{}/{}".format(
                    task.get("resource_info", {}).get("memory_allocated", "NaN"),
                    task.get("resource_info", {}).get("memory_total", "NaN"))
                task["schedule_start"] = task.get("schedule", {}).get("start_time", "")
                interval = task.get("schedule", {}).get("interval", {})
                task["schedule_interval"] = "{}{}".format(interval.get("value", ""), interval.get("unit", ""))
                task = obj_replace_time_field(task, ["create_time"])
                status_summary_running = status_format(task.get("lifecycle", ""), lifecycle_conf_ch,
                                                       "", dict(),
                                                       task.get("running_status", ""), running_status_conf_ch,
                                                       "task")
                task["status_summary_running"] = status_summary_running
                task_info = [task.get(key, "") for key in header]
                tasks_info.append(task_info)
            print_table(header.values(), tasks_info, auth.encoding)
        except Exception as e:
            raise

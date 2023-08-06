# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.task import Task as Task_base


lifecycle_conf_en = {"scheduling": "Scheduling",
                     "setting": "Setting"}
running_status_conf_en = {"idle": "Idle",
                          "running": "Running",
                          "success": "Success",
                          "failed": "Failed",
                          "killed": "Killed"}


class Task(object):
    @staticmethod
    def list(auth, appid):
        try:
            data = Task_base._list(auth, appid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Name"
            header["status_summary_running"] = "Status"
            header["application_id"] = "Application ID"
            header["cluster_id"] = "Cluster ID"
            header["cluster_name"] = "Cluster Name"
            header["version"] = "Version"
            header["prototype"] = "Prototype"
            header["cpu_allocated_total"] = "CPU Usage(cor)"
            header["memory_allocated_total"] = "Memory Usage(M)"
            header["schedule_start"] = "Schedule Start"
            header["schedule_interval"] = "Schedule Interval"
            header["create_time"] = "Create Time"
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
                status_summary_running = status_format(task.get("lifecycle", ""), lifecycle_conf_en,
                                                       "", dict(),
                                                       task.get("running_status", ""), running_status_conf_en,
                                                       "task")
                task["status_summary_running"] = status_summary_running
                task_info = [task.get(key, "") for key in header]
                tasks_info.append(task_info)
            print_table(header.values(), tasks_info, auth.encoding)
        except Exception as e:
            raise


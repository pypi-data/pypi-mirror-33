# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .base.task import Task as Task_base


class Task(object):
    @staticmethod
    def list(auth, appid):
        try:
            data = Task_base._list(auth, appid)
            tasks_info = []
            tasks = data.get("tasks", [])
            for task in tasks:
                task_info = dict(id=task.get("id", ""),
                                 name=task.get("name", ""),
                                 lifecycle=task.get("lifecycle", ""),
                                 running_status=task.get("running_status", ""),
                                 application_id=task.get("application_id", ""),
                                 cluster_id=task.get("cluster_id", ""),
                                 cluster_name=task.get("cluster_name", ""),
                                 version=task.get("version", ""),
                                 prototype=task.get("prototype", ""),
                                 resource_info=task.get("resource_info", ""),
                                 schedule=task.get("schedule", ""),
                                 create_time=task.get("create_time", ""),
                                 )
                task_info.get("resource_info", {}).pop("disk_allocated", "")
                task_info.get("resource_info", {}).pop("disk_total", "")
                tasks_info.append(task_info)
            print json.dumps(dict(tasks=tasks_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

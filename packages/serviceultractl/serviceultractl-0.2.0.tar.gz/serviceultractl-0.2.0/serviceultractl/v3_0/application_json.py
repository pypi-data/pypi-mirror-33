# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .base.application import Application as App_base


class Application(object):
    @staticmethod
    def list(auth):
        try:
            data = App_base._list(auth)
            applications_info = []
            applications = data.get("applications", [])
            users = data.get("users", {})
            for application in applications:
                application["creater_name"] = users.get(application.get("creater", ""), {}).get("nickname", "") \
                                              or users.get(application.get("creater", ""), {}).get("username", "")
                application_info = dict(id=application.get("id", ""),
                                        name=application.get("name", ""),
                                        lifecycle=application.get("lifecycle", ""),
                                        status_summary=application.get("status_summary", ""),
                                        running_status=application.get("running_status", ""),
                                        cpu_limit=application.get("cpu_limit", ""),
                                        memory_limit=application.get("memory_limit", ""),
                                        service_num=application.get("service_num", ""),
                                        service_running_num=application.get("service_running_num", ""),
                                        task_num=application.get("task_num", ""),
                                        task_running_num=application.get("task_running_num", ""),
                                        source=application.get("source", ""),
                                        creater_name=application.get("creater_name", ""),
                                        create_time=application.get("create_time", "")
                                        )
                applications_info.append(application_info)
            print json.dumps(dict(applications=applications_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, appid):
        try:
            data = App_base._show(auth, appid)
            application = data
            application_info = dict(id=application.get("id", ""),
                                    name=application.get("name", ""),
                                    lifecycle=application.get("lifecycle", ""),
                                    status_summary=application.get("status_summary", ""),
                                    running_status=application.get("running_status", ""),
                                    cpu_limit=application.get("cpu_limit", ""),
                                    memory_limit=application.get("memory_limit", ""),
                                    source=application.get("source", ""),
                                    create_time=application.get("create_time", "")
                                    )
            print json.dumps(application_info, indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def list_by_clusterid(auth, clusterid):
        try:
            data = App_base._list_by_clusterid(auth, clusterid)
            applications_info = []
            applications = data.get("applications", [])
            for application in applications:
                application_info = dict(id=application.get("id", ""),
                                        name=application.get("name", ""),
                                        lifecycle=application.get("lifecycle", ""),
                                        status_summary=application.get("status_summary", ""),
                                        running_status=application.get("running_status", ""),
                                        service_num=application.get("service_num", ""),
                                        task_num=application.get("task_num", ""),
                                        cpu_allocated=application.get("cpu_allocated", ""),
                                        cpu_limit=application.get("cpu_limit", ""),
                                        memory_allocated=application.get("memory_allocated", ""),
                                        memory_limit=application.get("memory_limit", ""),
                                        source=application.get("source", ""),
                                        create_time=application.get("create_time", "")
                                        )
                applications_info.append(application_info)
            print json.dumps(dict(applications=applications_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        try:
            data = App_base._statistics(auth)
            for cpu in data.get("ranks", {}).get("cpu", []):
                resource = cpu.get("resource_info", {})
                resource.pop("disk_allocated", "")
                resource.pop("disk_total", "")
            for memory in data.get("ranks", {}).get("memory", []):
                resource = memory.get("resource_info", {})
                resource.pop("disk_allocated", "")
                resource.pop("disk_total", "")
            print json.dumps(data, indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def entrance_list(auth, appid):
        try:
            data = App_base._entrance_list(auth, appid)
            entrances_info = []
            application_entrances = data.get("application_entrances", [])
            for application_entrance in application_entrances:
                entrance_info = dict(application_id=application_entrance.get("application_id", ""),
                                     service_id=application_entrance.get("service_id", ""),
                                     name=application_entrance.get("name", ""),
                                     url=application_entrance.get("url", "")
                                     )
                entrances_info.append(entrance_info)
            print json.dumps(dict(entrances=entrances_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

    @staticmethod
    def statistics_by_id(auth, appid):
        try:
            data = App_base._statistics_by_id(auth, appid)
            application = data[0] if len(data) > 0 else {}
            resource = application.get("resources", {})
            resource.pop("disk_allocated", "")
            resource.pop("disk_total", "")
            application.pop("application_id", "")
            print json.dumps(application, indent=4, ensure_ascii=False)
        except Exception as e:
            raise

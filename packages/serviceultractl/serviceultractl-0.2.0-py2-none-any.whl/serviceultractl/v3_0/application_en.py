# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field, status_format
from .base.application import Application as App_base


status_summary_conf_en = {"successfully_deployed": "Successfully deployed",
                          "failed_deployed": "Failed deployed",
                          "executing": "Executing",
                          "setting": "Setting"}
running_status_conf_en = {"green": "Normal",
                          "gray": "",
                          "yellow": "Warning",
                          "red": "Error"}
source_conf_en = {"du": "Su",
                  "saas": "SaaS"}


class Application(object):
    @staticmethod
    def list(auth):
        try:
            data = App_base._list(auth)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Name"
            header["status_summary_running"] = "Status"
            header["cpu_limit"] = "CPU limit(Cor)"
            header["memory_limit"] = "Memory limit(M)"
            header["service_num"] = "Service Num"
            header["service_running_num"] = "Running Service Num"
            header["task_num"] = "Task Num"
            header["task_running_num"] = "Running Task Num"
            header["source"] = "Source"
            header["creater_name"] = "Creator"
            header["create_time"] = "Create Time"
            applications_info = []
            applications = data.get("applications", [])
            users = data.get("users", {})
            for application in applications:
                application = obj_replace_time_field(application, ["create_time"])
                application["status_summary_running"] = status_format(application.get("lifecycle", ""),
                                                                      {},
                                                                      application.get("status_summary", ""),
                                                                      status_summary_conf_en,
                                                                      application.get("running_status", ""),
                                                                      running_status_conf_en,
                                                                      "application")
                application["source"] = source_conf_en.get(application.get("source", ""), u"")
                application["creater_name"] = users.get(application.get("creater", ""), {}).get("nickname", "") \
                                          or users.get(application.get("creater", ""), {}).get("username", "")
                application_info = [application.get(key, "") for key in header]
                applications_info.append(application_info)
            print_table(header.values(), applications_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def show(auth, appid):
        try:
            data = App_base._show(auth, appid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Name"
            header["status_summary_running"] = "Status"
            header["cpu_limit"] = "CPU limit(Cor)"
            header["memory_limit"] = "Memory limit(M)"
            header["source"] = "Source"
            header["create_time"] = "Create Time"
            applications_info = []
            application = data
            application = obj_replace_time_field(application, ["create_time"])
            application["status_summary_running"] = status_format(application.get("lifecycle", ""),
                                                                  {},
                                                                  application.get("status_summary", ""),
                                                                  status_summary_conf_en,
                                                                  application.get("running_status", ""),
                                                                  running_status_conf_en,
                                                                  "application")
            application["source"] = source_conf_en.get(application.get("source", ""), u"")
            application_info = [application.get(key, "") for key in header]
            applications_info.append(application_info)
            print_table(header.values(), applications_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def list_by_clusterid(auth, clusterid):
        try:
            data = App_base._list_by_clusterid(auth, clusterid)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Name"
            header["status_summary_running"] = "Status"
            header["service_num"] = "Service Num"
            header["task_num"] = "Task Num"
            header["cpu_allocated"] = "Allocated CPU"
            header["cpu_limit"] = "Total CPU"
            header["memory_allocated"] = "Allocated Memory(M)"
            header["memory_limit"] = "Total memory(M)"
            header["source"] = "Source"
            header["create_time"] = "Create Time"
            applications_info = []
            applications = data.get("applications", [])
            for application in applications:
                application = obj_replace_time_field(application, ["create_time"])
                application["status_summary_running"] = status_format(application.get("lifecycle", ""),
                                                                      {},
                                                                      application.get("status_summary", ""),
                                                                      status_summary_conf_en,
                                                                      application.get("running_status", ""),
                                                                      running_status_conf_en,
                                                                      "application")
                application["source"] = source_conf_en.get(application.get("source", ""), u"")
                application_info = [application.get(key, "") for key in header]
                applications_info.append(application_info)
            print_table(header.values(), applications_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def statistics(auth):
        try:
            data = App_base._statistics(auth)
            print "Applications Status:"
            header1 = collections.OrderedDict()
            header1["du"] = "Common Application"
            header1["saas"] = "SaaS Application"
            header1["error"] = "Error"
            header1["running"] = "Running"
            header1["setting"] = "Setting"
            header1["total"] = "Total"
            counts_info = []
            count = data.get("count", {})
            count_info = [count.get(key, "") for key in header1]
            counts_info.append(count_info)
            print_table(header1.values(), counts_info, auth.encoding)
            print u"Rank of CPU usages(cor):"
            header2 = collections.OrderedDict()
            header2["id"] = "ID"
            header2["name"] = "Name"
            header2["cpu_allocated"] = "Allocated CPU"
            header2["cpu_total"] = "Total CPU"
            cpus_info = []
            cpus = data.get("ranks", {}).get("cpu", [])
            for cpu in cpus:
                cpu.update(cpu.get("resource_info", {}))
                cpu_info = [cpu.get(key, "") for key in header2]
                cpus_info.append(cpu_info)
            print_table(header2.values(), cpus_info, auth.encoding)
            print u"Rank of Memory usages(M):"
            header3 = collections.OrderedDict()
            header3["id"] = "ID"
            header3["name"] = "Name"
            header3["memory_allocated"] = "Allocated Memory"
            header3["memory_total"] = "Total Memory"
            memorys_info = []
            memorys = data.get("ranks", {}).get("memory", [])
            for memory in memorys:
                memory.update(memory.get("resource_info", {}))
                memory_info = [memory.get(key, "") for key in header3]
                memorys_info.append(memory_info)
            print_table(header3.values(), memorys_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def entrance_list(auth, appid):
        try:
            data = App_base._entrance_list(auth, appid)
            header = collections.OrderedDict()
            header["application_id"] = "Application ID"
            header["service_id"] = "Service ID"
            header["name"] = "Entrance Name"
            header["url"] = "Url"
            entrances_info = []
            application_entrances = data.get("application_entrances", [])
            for application_entrance in application_entrances:
                entrance_info = [application_entrance.get(key, "") for key in header]
                entrances_info.append(entrance_info)
            print_table(header.values(), entrances_info, auth.encoding)
        except Exception as e:
            raise

    @staticmethod
    def statistics_by_id(auth, appid):
        try:
            data = App_base._statistics_by_id(auth, appid)
            print "Resource Status:"
            header1 = collections.OrderedDict()
            header1["application_id"] = "Application ID"
            header1["cpu_allocated"] = "Allocated CPU(cor)"
            header1["cpu_total"] = "Total CPU"
            header1["memory_allocated"] = "Allocated Memory(M)"
            header1["memory_total"] = "Total Memory"
            resources_info = []
            apps = data
            for app in apps:
                app.update(app.get("resources", {}))
                resource_info = [app.get(key, "") for key in header1]
                resources_info.append(resource_info)
            print_table(header1.values(), resources_info, auth.encoding)
            print "Service Running Status:"
            header2 = collections.OrderedDict()
            header2["running"] = "Running"
            header2["setting"] = "Setting"
            header2["total"] = "Total"
            services_info = []
            for app in apps:
                app.update(app.get("services", {}))
                service_info = [app.get(key, "") for key in header2]
                services_info.append(service_info)
            print_table(header2.values(), services_info, auth.encoding)
            print u"Task Running Status:"
            header3 = collections.OrderedDict()
            header3["running"] = "Running"
            header3["setting"] = "Setting"
            header3["total"] = "Total"
            tasks_info = []
            for app in apps:
                app.update(app.get("tasks", {}))
                task_info = [app.get(key, "") for key in header3]
                tasks_info.append(task_info)
            print_table(header3.values(), tasks_info, auth.encoding)
        except Exception as e:
            raise


# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.cluster import ClusterDispatch as Cluster
from .v3_0.commonnode import CommonNodeDispatch as CN
from .v3_0.application import ApplicationDispatch as Application
from .v3_0.service import ServiceDispatch as Service
from .v3_0.task import TaskDispatch as Task
from .v3_0.microservice import MicroServiceDispatch as MicroService
from .v3_0.instance import InstanceDispatch as Instance
from .v3_0.file import FileDispatch as File
from .v3_0.my_application import MyApplicationDispatch as MyApplication


class LsCommands(object):
    @args("--clusterid", dest="clusterid", default=None, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def cluster(self, auth, clusterid=None, format_json=False):
        """list clusters info"""
        if clusterid:
            Cluster.show(auth, clusterid, format_json)
        else:
            Cluster.list(auth, format_json)

    @args("--machineid", dest="machineid", default=None, help="")
    @args("--clusterid", dest="clusterid", default=None, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def machine(self, auth, machineid=None, clusterid=None, format_json=False):
        """list machines info"""
        if not machineid and not clusterid:
            CN.list(auth, format_json)
        elif not clusterid:
            CN.show(auth, machineid, format_json)
        elif not machineid:
            CN.list_by_clusterid(auth, clusterid, format_json)
        else:
            raise Exception("Parameter error")

    @args("--appid", dest="appid", default=None, help="")
    @args("--clusterid", dest="clusterid", default=None, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def application(self, auth, appid=None, clusterid=None, format_json=False):
        """list applications info"""
        if not appid and not clusterid:
            Application.list(auth, format_json)
        elif not clusterid:
            Application.show(auth, appid, format_json)
        elif not appid:
            Application.list_by_clusterid(auth, clusterid, format_json)
        else:
            raise Exception("Parameter error")

    @args("--appid", dest="appid", required=True, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def service(self, auth, appid, format_json=False):
        """list services info"""
        Service.list(auth, appid, format_json)

    @args("--appid", dest="appid", required=True, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def task(self, auth, appid, format_json=False):
        """list tasks info"""
        Task.list(auth, appid, format_json)

    @args("--serviceid", dest="serviceid", required=True, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def microservice(self, auth, serviceid, format_json=False):
        """list micro services info"""
        MicroService.list(auth, serviceid, format_json)

    @args("--serviceid", dest="serviceid", required=True, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def instance(self, auth, serviceid, format_json=False):
        """list instances info"""
        Instance.list(auth, serviceid, format_json)

    @args("--appid", dest="appid", required=True, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def entrance(self, auth, appid, format_json=False):
        """list application's entrances info"""
        Application.entrance_list(auth, appid, format_json)

    @args("--path", dest="path", default="/", help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def file(self, auth, path="/", format_json=False):
        """list files on file manager"""
        File.list(auth, path, format_json)

    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def myapp(self, auth, format_json=False):
        MyApplication.list(auth, format_json)

    # @args("--serviceid", dest="serviceid", required=True, help=u"实例对应的服务id")
    # @args("--instanceid", dest="instanceid", help=u"实例id")
    # @args("-t", dest="terminal_flag", default=False, action='store_true', help=u"开启终端,必须输入instanceid及serviceid")
    # @args("-l", dest="log_flag", default=False, action='store_true', help=u"查看日志,必须输入instanceid及serviceid")
    # def instance(self, auth, serviceid, instanceid, terminal_flag, log_flag):
    #     """显示实例列表"""
    #     if terminal_flag and log_flag:
    #         raise Exception("Parameter error")
    #     elif not terminal_flag and not log_flag:
    #         Instance.list(auth, serviceid)
    #     elif not log_flag:
    #         Instance.terminal(auth, serviceid, instanceid)
    #     else:
    #         Instance.log(auth, serviceid, instanceid)


    # @args("--serviceid", dest="serviceid", required=True, help=u"根据服务id查询实例")
    # @args("--instanceid", dest="instanceid", required=True, help=u"根据实例id查询log")
    # def instance_log(self, auth, servieid, instanceid):
    #     """显示实例日志"""
    #     Instance.log(auth, servieid, instanceid)
    #
    # @args("--serviceid", dest="serviceid", required=True, help=u"根据服务id查询实例")
    # @args("--instanceid", dest="instanceid", required=True, help=u"根据实例id查询log")
    # def instance_terminal(self, auth, servieid, instanceid):
    #     """显示实例日志"""
    #     Instance.terminal(auth, servieid, instanceid)
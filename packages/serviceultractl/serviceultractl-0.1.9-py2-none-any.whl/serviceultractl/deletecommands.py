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


class DeleteCommands(object):
    @args("--clusterid", dest="clusterid", required=True, help="")
    def cluster(self, auth, clusterid):
        """delete cluster"""
        Cluster.delete(auth, clusterid)

    @args("--machineid", dest="machineids", required=True, nargs="+", help="")
    def machine(self, auth, machineids):
        """delete machine"""
        CN.delete_batch(auth, machineids)

    @args("--appid", dest="appid", required=True, help="")
    def application(self, auth, appid):
        """delete application"""
        Application.delete(auth, appid)

    @args("--serviceid", dest="serviceids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    def service(self, auth, serviceids, appid):
        """delete service"""
        Service.delete_batch(auth, appid, serviceids)

    # @args("--taskid", dest="taskids", required=True, nargs="+", help=u"任务ID")
    # @args("--appid", dest="appid", required=True, help=u"所属应用ID")
    # def task(self, auth, taskids, appid):
    #     """删除任务"""
    #     Task.delete_batch(auth, appid, taskids)
    @args("--taskid", dest="taskids", required=True, nargs="+", help="")
    def task(self, auth, taskids):
        """delete task"""
        Task.delete_batch(auth, taskids)

    @args("--microserviceid", dest="microserviceids", required=True, nargs="+", help="")
    @args("--serviceid", dest="serviceid", required=True, help="")
    def microservice(self, auth, microserviceids, serviceid):
        """delete micro service"""
        MicroService.delete_batch(auth, serviceid, microserviceids)

    @args("--instanceid", dest="instanceids", required=True, nargs="+", help="")
    @args("--microserviceid", dest="microserviceid", required=True, help="")
    @args("--serviceid", dest="serviceid", required=True, help="")
    def instance(self, auth, instanceids, microserviceid, serviceid):
        """delete instance"""
        Instance.delete_batch(auth, serviceid, microserviceid, instanceids)

    @args("--path", dest="paths", nargs="+", required=True, help="full path of file")
    def file(self, auth, paths):
        """delete files"""
        File.delete_batch(auth, paths)


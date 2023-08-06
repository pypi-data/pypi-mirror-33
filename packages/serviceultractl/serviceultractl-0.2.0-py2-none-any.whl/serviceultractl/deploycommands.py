# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.commonnode import CommonNodeDispatch as CN
from .v3_0.service import ServiceDispatch as Service
from .v3_0.task import TaskDispatch as Task
from .v3_0.instance import InstanceDispatch as Instance


class DeployCommands(object):
    @args("--machineid", dest="machineids", required=True, nargs="+", help="")
    @args("--clusterid", dest="clusterid", required=True, help="")
    @args("--timeout", dest="timeout", type=int, default=200, help='set timeout when sync is True')
    @args("--sync", dest="sync", type=bool, default=False, choices=[True, False], help='wait for callback when sync is True')
    def machine(self, auth, machineids, clusterid, timeout=200, sync=False):
        """deploy machine"""
        if sync and not timeout:
            raise Exception("please set timeout when sync")
        CN.deploy_batch(auth, clusterid, machineids, timeout, sync)

    @args("--serviceid", dest="serviceids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    @args("--timeout", dest="timeout", type=int, default=200, help='set timeout when sync is True')
    @args("--sync", dest="sync", type=bool, default=False, choices=[True, False], help='wait for callback when sync is True')
    def service(self, auth, serviceids, appid, timeout=200, sync=False):
        """deploy service"""
        if sync and not timeout:
            raise Exception("please set timeout when sync")
        Service.deploy_batch(auth, appid, serviceids, timeout, sync)

    @args("--instanceid", dest="instanceids", required=True, nargs="+", help="")
    @args("--microserviceid", dest="microserviceid", required=True, help="")
    @args("--serviceid", dest="serviceid", required=True, help="")
    @args("--timeout", dest="timeout", type=int, default=200, help='set timeout when sync is True')
    @args("--sync", dest="sync", type=bool, default=False, choices=[True, False], help='wait for callback when sync is True')
    def instance(self, auth, instanceids, microserviceid, serviceid, timeout=200, sync=False):
        """deploy instance"""
        if sync and not timeout:
            raise Exception("please set timeout when sync")
        Instance.deploy_batch(auth, serviceid, microserviceid, instanceids, timeout, sync)

    @args("--taskid", dest="taskids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    def task(self, auth, taskids, appid):
        """deploy task"""
        Task.deploy_batch(auth, appid, taskids)

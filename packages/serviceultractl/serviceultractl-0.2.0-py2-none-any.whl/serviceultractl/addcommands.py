# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.commonnode import CommonNodeDispatch as CN
from .v3_0.instance import InstanceDispatch as Instance


class AddCommands(object):
    @args("--virtual_node_num", dest="virtual_node_num", default=1, help=u"虚拟节点数")
    @args("--machineid", dest="machineids", required=True, nargs="+", help=u"主机ID")
    @args("--clusterid", dest="clusterid", required=True, help=u"所属集群ID")
    def machine(self, auth, virtual_node_num, machineids, clusterid):
        """add machine to cluster"""
        CN.add_batch(auth, clusterid, machineids, virtual_node_num)

    @args("--instanceid", dest="instanceids", required=True, nargs="+", help=u"实例ID")
    @args("--microserviceid", dest="microserviceuid", required=True, help=u"所属微服务ID")
    @args("--serviceid", dest="serviceid", required=True, help=u"所属服务ID")
    def instance(self, auth, instanceids, microserviceid, serviceid):
        """add instance"""
        Instance.add_batch(auth, serviceid, microserviceid, instanceids)
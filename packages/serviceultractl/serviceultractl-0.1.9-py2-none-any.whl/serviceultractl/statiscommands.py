# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.cluster import ClusterDispatch as Cluster
from .v3_0.commonnode import CommonNodeDispatch as CN
from .v3_0.application import ApplicationDispatch as Application
from .v3_0.microservice import MicroServiceDispatch as MicroService


class StatisCommands(object):
    @args("--clusterid", dest="clusterid", default=None, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def cluster(self, auth, clusterid=None, format_json=False):
        """statistics info of clusters"""
        if clusterid:
            Cluster.statistics_by_id(auth, clusterid, format_json)
        else:
            Cluster.statistics(auth, format_json)

    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def machine(self, auth, format_json=False):
        """statistics info of machines"""
        CN.statistics(auth, format_json)

    @args("--appid", dest="appid", default=None, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def application(self, auth, appid=None, format_json=False):
        """statistics info of applications"""
        if appid:
            Application.statistics_by_id(auth, appid, format_json)
        else:
            Application.statistics(auth, format_json)

    @args("--serviceid", dest="serviceid", required=True, help="")
    @args("-f", dest="format_json", default=False, action='store_true', help="return data in JSON format")
    def microservice(self, auth, serviceid, format_json=False):
        """statistics info of micro services"""
        MicroService.statistics(auth, serviceid, format_json)


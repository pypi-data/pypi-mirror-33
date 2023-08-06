# -*- coding: utf-8 -*-
from .cluster_ch import Cluster as Cluster_ch
from .cluster_en import Cluster as Cluster_en
from .cluster_json import Cluster as Cluster_json
from .base.cluster import Cluster as Cluster_base


class ClusterDispatch(object):
    @staticmethod
    def list(auth, format_json):
        if format_json:
            Cluster_json.list(auth)
        else:
            if auth.language == "en":
                Cluster_en.list(auth)
            else:
                Cluster_ch.list(auth)

    @staticmethod
    def show(auth, clusterid, format_json):
        if format_json:
            Cluster_json.show(auth, clusterid)
        else:
            if auth.language == "en":
                Cluster_en.show(auth, clusterid)
            else:
                Cluster_ch.show(auth, clusterid)

    @staticmethod
    def statistics_by_id(auth, clusterid, format_json):
        if format_json:
            Cluster_json.statistics_by_id(auth, clusterid)
        else:
            if auth.language == "en":
                Cluster_en.statistics_by_id(auth, clusterid)
            else:
                Cluster_ch.statistics_by_id(auth, clusterid)

    @staticmethod
    def statistics(auth, format_json):
        if format_json:
            Cluster_json.statistics(auth)
        else:
            if auth.language == "en":
                Cluster_en.statistics(auth)
            else:
                Cluster_ch.statistics(auth)

    @staticmethod
    def delete(auth, clusterid):
        Cluster_base._delete(auth, clusterid)








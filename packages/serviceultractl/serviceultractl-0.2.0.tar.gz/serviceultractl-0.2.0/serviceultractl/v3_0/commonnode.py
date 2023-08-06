# -*- coding: utf-8 -*-
from .commonnode_ch import CommonNode as Node_ch
from .commonnode_en import CommonNode as Node_en
from .commonnode_json import CommonNode as Node_json
from .base.commonnode import CommonNode as Node_base


class CommonNodeDispatch(object):
    @staticmethod
    def list(auth, format_json):
        if format_json:
            Node_json.list(auth)
        else:
            if auth.language == "en":
                Node_en.list(auth)
            else:
                Node_ch.list(auth)

    @staticmethod
    def show(auth, machineid, format_json):
        if format_json:
            Node_json.show(auth, machineid)
        else:
            if auth.language == "en":
                Node_en.show(auth, machineid)
            else:
                Node_ch.show(auth, machineid)

    @staticmethod
    def list_by_clusterid(auth, clusterid, format_json):
        if format_json:
            Node_json.list_by_clusterid(auth, clusterid)
        else:
            if auth.language == "en":
                Node_en.list_by_clusterid(auth, clusterid)
            else:
                Node_ch.list_by_clusterid(auth, clusterid)

    @staticmethod
    def statistics(auth, format_json):
        if format_json:
            Node_json.statistics(auth)
        else:
            if auth.language == "en":
                Node_en.statistics(auth)
            else:
                Node_ch.statistics(auth)

    @staticmethod
    def deploy_batch(auth, clusterid, machineids):
        Node_base._deploy_batch(auth, clusterid, machineids)

    @staticmethod
    def undeploy_batch(auth, clusterid, machineids):
        Node_base._undeploy_batch(auth, clusterid, machineids)

    @staticmethod
    def delete_batch(auth, machineids):
        Node_base._delete_batch(auth, machineids)

    @staticmethod
    def add_batch(auth, clusterid, machineids, virtual_node_num):
        Node_base._add_batch(auth, clusterid, machineids, virtual_node_num)

    @staticmethod
    def remove_batch(auth, clusterid, machineids):
        Node_base._remove_batch(auth, clusterid, machineids)












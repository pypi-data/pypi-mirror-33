# -*- coding: utf-8 -*-
from .microservice_ch import MicroService as Ms_ch
from .microservice_en import MicroService as Ms_en
from .microservice_json import MicroService as Ms_json
from .base.microservice import MicroService as Ms_base


class MicroServiceDispatch(object):
    @staticmethod
    def list(auth, serviceid, format_json):
        """根据服务ID显示该服务下微服务列表"""
        if format_json:
            Ms_json.list(auth, serviceid)
        else:
            if auth.language == "en":
                Ms_en.list(auth, serviceid)
            else:
                Ms_ch.list(auth, serviceid)

    @staticmethod
    def statistics(auth, serviceid, format_json):
        if format_json:
            Ms_json.statistics(auth, serviceid)
        else:
            if auth.language == "en":
                Ms_en.statistics(auth, serviceid)
            else:
                Ms_ch.statistics(auth, serviceid)

    @staticmethod
    def delete_batch(auth, serviceid, microserviceids):
        """批量删除微服务"""
        Ms_base._delete_batch(auth, serviceid, microserviceids)

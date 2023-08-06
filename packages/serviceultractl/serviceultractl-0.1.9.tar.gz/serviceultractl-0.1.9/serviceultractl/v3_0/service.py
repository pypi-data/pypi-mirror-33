# -*- coding: utf-8 -*-
from .service_ch import Service as Srv_ch
from .service_en import Service as Srv_en
from .service_json import Service as Srv_json
from .base.service import Service as Srv_base
from .base.common import Common


class ServiceDispatch(object):
    @staticmethod
    def list(auth, appid, format_json):
        """根据应用ID显示该应用下服务列表"""
        if format_json:
            Srv_json.list(auth, appid)
        else:
            if auth.language == "en":
                Srv_en.list(auth, appid)
            else:
                Srv_ch.list(auth, appid)

    @staticmethod
    def deploy_batch(auth, appid, serviceids, timeout, sync):
        """服务上线"""
        job_id = Srv_base._deploy_batch(auth, appid, serviceids)
        if sync:
            status = Common._job_check(timeout, auth, job_id)
            if status == "success":
                print "deploy {} successfully".format(','.join(serviceids))
            else:
                raise Exception("deploy {} fail".format(','.join(serviceids)))

    @staticmethod
    def redeploy_batch(auth, appid, serviceids, timeout, sync):
        """服务上线"""
        job_id = Srv_base._redeploy_batch(auth, appid, serviceids)
        if sync:
            status = Common._job_check(timeout, auth, job_id)
            if status == "success":
                print "redeploy {} successfully".format(','.join(serviceids))
            else:
                raise Exception("redeploy {} fail".format(','.join(serviceids)))

    @staticmethod
    def undeploy_batch(auth, appid, serviceids, timeout, sync):
        """服务下线"""
        job_id = Srv_base._undeploy_batch(auth, appid, serviceids)
        if sync:
            status = Common._job_check(timeout, auth, job_id)
            if status == "success":
                print "undeploy {} successfully".format(','.join(serviceids))
            else:
                raise Exception("undeploy {} fail".format(','.join(serviceids)))

    @staticmethod
    def delete_batch(auth, appid, serviceids):
        """批量删除服务"""
        Srv_base._delete_batch(auth, appid, serviceids)

    # @staticmethod
    # def delete(auth, serviceid):
    #     """删除服务"""
    #     print("delete service")

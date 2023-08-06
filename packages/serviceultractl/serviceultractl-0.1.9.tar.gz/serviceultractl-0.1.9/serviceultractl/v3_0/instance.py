# -*- coding: utf-8 -*-
from .instance_ch import Instance as Ins_ch
from .instance_en import Instance as Ins_en
from .instance_json import Instance as Ins_json
from .base.instance import Instance as Ins_base
from .base.common import Common


class InstanceDispatch(object):
    @staticmethod
    def list(auth, serviceid, format_json):
        """根据服务ID显示该应用下实例列表"""
        if format_json:
            Ins_json.list(auth, serviceid)
        else:
            if auth.language == "en":
                Ins_en.list(auth, serviceid)
            else:
                Ins_ch.list(auth, serviceid)

    @staticmethod
    def deploy_batch(auth, serviceid, microserviceid, instanceids, timeout, sync):
        """部署实例"""
        job_id = Ins_base._deploy_batch(auth, serviceid, microserviceid, instanceids)
        if sync:
            status = Common._job_check(timeout, auth, job_id)
            if status == "success":
                print "deploy {} successfully".format(','.join(instanceids))
            else:
                raise Exception("deploy {} fail".format(','.join(instanceids)))

    @staticmethod
    def undeploy_batch(auth, serviceid, microserviceid, instanceids, timeout, sync):
        """卸载实例"""
        job_id = Ins_base._undeploy_batch(auth, serviceid, microserviceid, instanceids)
        if sync:
            status = Common._job_check(timeout, auth, job_id)
            print status
            if status == "success":
                print "undeploy {} successfully".format(','.join(instanceids))
            else:
                raise Exception("undeploy {} fail".format(','.join(instanceids)))

    @staticmethod
    def delete_batch(auth, serviceid, microserviceid, instanceids):
        """批量删除实例"""
        Ins_base._delete_batch(auth, serviceid, microserviceid, instanceids)

    @staticmethod
    def add_batch(auth, serviceid, microserviceid, instanceids):
        """批量添加实例"""
        print("Developing...")

    @staticmethod
    def log(auth, instanceid):
        """实例日志"""
        Ins_base._log(auth, instanceid)

    @staticmethod
    def terminal(auth, instanceid):
        """实例终端"""
        Ins_base._terminal(auth, instanceid)
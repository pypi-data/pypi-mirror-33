# -*- coding: utf-8 -*-
from .task_ch import Task as Task_ch
from .task_en import Task as Task_en
from .task_json import Task as Task_json
from .base.task import Task as Task_base


class TaskDispatch(object):
    @staticmethod
    def list(auth, appid, format_json):
        """根据应用ID显示该应用下任务列表"""
        if format_json:
            Task_json.list(auth, appid)
        else:
            if auth.language == "en":
                Task_en.list(auth, appid)
            else:
                Task_ch.list(auth, appid)

    @staticmethod
    def deploy_batch(auth, appid, taskids):
        """任务上线"""
        Task_base._deploy_batch(auth, appid, taskids)

    @staticmethod
    def undeploy_batch(auth, appid, taskids):
        """任务下线"""
        Task_base._undeploy_batch(auth, appid, taskids)

    @staticmethod
    def start_batch(auth, appid, taskids):
        """启动任务"""
        Task_base._start_batch(auth, appid, taskids)

    @staticmethod
    def stop_batch(auth, appid, taskids):
        """停止任务"""
        Task_base._stop_batch(auth, appid, taskids)

    @staticmethod
    def delete_batch(auth, taskids):
        """删除任务"""
        Task_base._delete_batch(auth, taskids)


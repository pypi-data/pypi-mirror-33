# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.task import TaskDispatch as Task


class StopCommands(object):
    @args("--taskid", dest="taskids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    def task(self, auth, taskids, appid):
        """stop task"""
        Task.stop_batch(auth, appid, taskids)

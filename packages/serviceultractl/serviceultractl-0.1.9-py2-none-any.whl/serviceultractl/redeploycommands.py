# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.service import ServiceDispatch as Service


class RedeployCommands(object):
    @args("--serviceid", dest="serviceids", required=True, nargs="+", help="")
    @args("--appid", dest="appid", required=True, help="")
    @args("--timeout", dest="timeout", type=int, default=200, help='set timeout when sync is True')
    @args("--sync", dest="sync", type=bool, default=False, choices=[True, False], help='wait for callback when sync is True')
    def service(self, auth, serviceids, appid, timeout=200, sync=False):
        """redeploy service"""
        if sync and not timeout:
            raise Exception("please set timeout when sync")
        Service.redeploy_batch(auth, appid, serviceids, timeout, sync)



# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.my_application import MyApplicationDispatch as myApp


class ExportCommands(object):
    @args("--appid", dest="appid", required=True, help="appid of exported app")
    @args("--name", dest="apkname", required=True, help="apk name")
    @args("--version", dest="version", required=True, help="apk version")
    @args("--description", dest="description", default="", help="apk description")
    def myapp(self, auth, appid, apkname, version, description):
        """export app to apk"""
        myApp.export(auth, appid, apkname, version, description)


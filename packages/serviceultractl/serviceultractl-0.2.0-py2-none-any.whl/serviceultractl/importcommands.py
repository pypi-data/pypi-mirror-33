# -*- coding: utf-8 -*-
from .utils.parse_utils import args
from .v3_0.my_application import MyApplicationDispatch as myApp


class ImportCommands(object):
    @args("--apkid", dest="apkid", required=True, help="id of imported apk")
    @args("--clusterid", dest="clusterid", required=True, help="select cluster to deploy")
    @args("--appname", dest="applicationname", required=True, help="application name")
    def myapp(self, auth, apkid, clusterid, applicationname):
        """import apk to app"""
        myApp._import(auth, apkid, clusterid, applicationname)


# -*- coding: utf-8 -*-
from .my_application_ch import MyApplication as myApp_ch
from .my_application_en import MyApplication as myApp_en
from .my_application_json import MyApplication as myApp_json
from .base.my_application import MyApplication as myApp_base


class MyApplicationDispatch(object):
    @staticmethod
    def list(auth, format_json):
        if format_json:
            myApp_json.list(auth)
        else:
            if auth.language == "en":
                myApp_en.list(auth)
            else:
                myApp_ch.list(auth)

    @staticmethod
    def export(auth, appid, apkname, version, description):
        myApp_base._export(auth, appid, apkname, version, description)

    @staticmethod
    def _import(auth, apkid, clusterid, applicationname):
        myApp_base._import(auth, apkid, clusterid, applicationname)

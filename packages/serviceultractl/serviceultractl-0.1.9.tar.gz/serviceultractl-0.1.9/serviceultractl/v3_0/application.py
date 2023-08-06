# -*- coding: utf-8 -*-
from .application_ch import Application as App_ch
from .application_en import Application as App_en
from .application_json import Application as App_json
from .base.application import Application as App_base


class ApplicationDispatch(object):
    @staticmethod
    def list(auth, format_json):
        if format_json:
            App_json.list(auth)
        else:
            if auth.language == "en":
                App_en.list(auth)
            else:
                App_ch.list(auth)

    @staticmethod
    def show(auth, appid, format_json):
        if format_json:
            App_json.show(auth, appid)
        else:
            if auth.language == "en":
                App_en.show(auth, appid)
            else:
                App_ch.show(auth, appid)

    @staticmethod
    def list_by_clusterid(auth, clusterid, format_json):
        if format_json:
            App_json.list_by_clusterid(auth, clusterid)
        else:
            if auth.language == "en":
                App_en.list_by_clusterid(auth, clusterid)
            else:
                App_ch.list_by_clusterid(auth, clusterid)

    @staticmethod
    def statistics(auth, format_json):
        if format_json:
            App_json.statistics(auth)
        else:
            if auth.language == "en":
                App_en.statistics(auth)
            else:
                App_ch.statistics(auth)

    @staticmethod
    def entrance_list(auth, appid, format_json):
        if format_json:
            App_json.entrance_list(auth, appid)
        else:
            if auth.language == "en":
                App_en.entrance_list(auth, appid)
            else:
                App_ch.entrance_list(auth, appid)

    @staticmethod
    def statistics_by_id(auth, appid, format_json):
        if format_json:
            App_json.statistics_by_id(auth, appid)
        else:
            if auth.language == "en":
                App_en.statistics_by_id(auth, appid)
            else:
                App_ch.statistics_by_id(auth, appid)

    @staticmethod
    def delete(auth, appid):
        App_base._delete(auth, appid)

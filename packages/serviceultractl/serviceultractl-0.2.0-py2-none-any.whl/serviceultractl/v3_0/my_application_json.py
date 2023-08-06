# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from .base.my_application import MyApplication as myApp_base


class MyApplication(object):
    @staticmethod
    def list(auth):
        try:
            data = myApp_base._list(auth)
            application_pks_info = []
            for _ in data:
                for application_pk in _.get("applicationPks", []):
                    application_pk_info = dict(id=application_pk.get("id", ""),
                                               name=application_pk.get("name", ""),
                                               version=application_pk.get("versionName", ""),
                                               buildStatus=application_pk.get("buildStatus", ""),
                                               createdTime=application_pk.get("createdTime", ""))
                    application_pks_info.append(application_pk_info)
            print json.dumps(dict(application_pks=application_pks_info), indent=4, ensure_ascii=False)
        except Exception as e:
            raise

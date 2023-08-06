# -*- coding: utf-8 -*-
import collections
from ..utils.common_utils import print_table, obj_replace_time_field
from .base.my_application import MyApplication as myApp_base


buildStatus_en = {"SUCCESS": "Success",
                  "FAILED": "Failed",
                  "ING": "Building"}


class MyApplication(object):
    @staticmethod
    def list(auth):
        try:
            data = myApp_base._list(auth)
            header = collections.OrderedDict()
            header["id"] = "ID"
            header["name"] = "Name"
            header["versionName"] = "Version"
            header["buildStatus"] = "Build Status"
            header["createdTime"] = "Create Time"
            application_pks_info = []
            for _ in data:
                for application_pk in _.get("applicationPks", []):
                    application_pk = obj_replace_time_field(application_pk, ["createdTime"])
                    application_pk["buildStatus"] = buildStatus_en.get(application_pk.get("buildStatus", ""), "")
                    application_pk_info = [application_pk.get(key, "") for key in header]
                    application_pks_info.append(application_pk_info)
            print_table(header.values(), application_pks_info, auth.encoding)
        except Exception as e:
            raise


# -*- coding: utf-8 -*-
import json
from ...utils.http_utils import http_request


class MyApplication(object):
    @staticmethod
    def _list(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/application/v1/application")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        status, response_data = http_request(url=url, http_method=http_method, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        return data

    @staticmethod
    def _export(auth, appid, apkname, version, description):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/application/v1/application")
        http_method = "POST"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_data = json.dumps(dict(applicationId=appid,
                                        detail="",
                                        name=apkname,
                                        picture="fa fa-cloud te-bg-1",
                                        versionDescription=description,
                                        versionName=version))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_data, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print (u"Export application {} complete".format(appid))
        except Exception as e:
            raise

    @staticmethod
    def _import(auth, apkid, clusterid, applicationname):
        data = MyApplication._show(auth, apkid)
        application_file_path = data.get("zipUrl", "")
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/application/v1/application/import")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_data = json.dumps(dict(applicationName=applicationname,
                                       application_file_path=application_file_path,
                                       clusterId=clusterid,
                                       description="",
                                       tags=[]))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_data, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print (u"Import apk {} complete".format(apkid))
        except Exception as e:
            raise

    @staticmethod
    def _show(auth, apkid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/application/v1/application", apkid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        status, response_data = http_request(url=url, http_method=http_method, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Authorization Error")
            raise Exception(message)
        return data

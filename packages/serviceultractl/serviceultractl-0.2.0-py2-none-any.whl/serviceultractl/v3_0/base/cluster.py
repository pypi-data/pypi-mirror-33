# -*- coding: utf-8 -*-
import json
from ...utils.http_utils import http_request


class Cluster(object):
    @staticmethod
    def _list(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/misc/v1/clusters")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        status, response_data = http_request(url=url, http_method=http_method, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        return data

    @staticmethod
    def _show(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/clusters", clusterid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        status, response_data = http_request(url=url, http_method=http_method, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        return data

    @staticmethod
    def _statistics_by_id(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url1 = "{}://{}{}?type=cluster&ids={}".format(security, address, "/dispatch/platform/v1/statistics", clusterid)
        url2 = "{}://{}{}/{}".format(security, address, "/dispatch/nodemonitor/v1/clusters", clusterid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        status, response_data = http_request(url=url1, http_method=http_method, headers=headers)
        data1 = json.loads(response_data)
        if status != 200:
            message = data1.get("message", "Unknown Error")
            raise Exception(message)
        status, response_data = http_request(url=url2, http_method=http_method, headers=headers)
        data2 = json.loads(response_data)
        if status != 200:
            message = data2.get("message", "Unknown Error")
            raise Exception(message)
        return data1, data2

    @staticmethod
    def _statistics(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/cluster_statistics")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        status, response_data = http_request(url=url, http_method=http_method, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        return data

    @staticmethod
    def _delete(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/clusters", clusterid)
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_data = json.dumps(dict())
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_data, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print (u"Delete cluster {} complete".format(clusterid))
        except Exception as e:
            raise








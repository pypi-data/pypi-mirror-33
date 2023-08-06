# -*- coding: utf-8 -*-
import json
from ...utils.http_utils import http_request


class Service(object):
    @staticmethod
    def _list(auth, appid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?application_id={}".format(security, address, "/dispatch/platform/v1/services", appid)
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
    def _deploy_batch(auth, appid, serviceids):
        """服务上线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/services/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=serviceids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"服务 {} 上线指令发送成功".format(','.join(serviceids)))
            print (u'Send "deploy {}" successfully'.format(','.join(serviceids)))
            return data.get("job_id", "")
        except Exception as e:
            raise

    @staticmethod
    def _redeploy_batch(auth, appid, serviceids):
        """服务上线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/services/redeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=serviceids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"服务 {} 上线指令发送成功".format(','.join(serviceids)))
            print (u'Send "redeploy {}" successfully'.format(','.join(serviceids)))
        except Exception as e:
            raise

    @staticmethod
    def _undeploy_batch(auth, appid, serviceids):
        """服务下线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/services/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=serviceids,
                                       application_id=appid,
                                       delete_data=True))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print (u'Send "undeploy {}" successfully'.format(','.join(serviceids)))
            return data.get("job_id", "")
        except Exception as e:
            raise

    @staticmethod
    def _delete_batch(auth, appid, serviceids):
        """批量删除服务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/services")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=serviceids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print (u"Delete service {} complete".format(','.join(serviceids)))
        except Exception as e:
            raise

    # @staticmethod
    # def delete(auth, serviceid):
    #     """删除服务"""
    #     print("delete service")

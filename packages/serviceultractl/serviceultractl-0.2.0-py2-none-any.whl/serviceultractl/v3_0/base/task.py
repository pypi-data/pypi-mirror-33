# -*- coding: utf-8 -*-
import json
from ...utils.http_utils import http_request


class Task(object):
    @staticmethod
    def _list(auth, appid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?application_id={}".format(security, address, "/dispatch/platform/v1/tasks", appid)
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
    def _deploy_batch(auth, appid, taskids):
        """任务上线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"任务 {} 上线指令发送成功".format(','.join(taskids)))
            print (u"Deploy {} successfully".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def _undeploy_batch(auth, appid, taskids):
        """任务下线"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"任务 {} 下线指令发送成功".format(','.join(taskids)))
            print (u"Undeploy {} successfully".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def _start_batch(auth, appid, taskids):
        """启动任务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/start")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"任务 {} 启动指令发送成功".format(','.join(taskids)))
            print (u"start task {} successfully".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def _stop_batch(auth, appid, taskids):
        """停止任务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks/stop")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids,
                                       application_id=appid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"任务 {} 停止指令发送成功".format(','.join(taskids)))
            print (u"Stop task {} successfully".format(','.join(taskids)))
        except Exception as e:
            raise

    @staticmethod
    def _delete_batch(auth, taskids):
        """删除任务"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/tasks")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=taskids))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print (u"Delete task {} complete".format(','.join(taskids)))
        except Exception as e:
            raise


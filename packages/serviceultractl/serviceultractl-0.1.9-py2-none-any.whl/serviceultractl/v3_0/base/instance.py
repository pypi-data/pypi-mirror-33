# -*- coding: utf-8 -*-
import json
import os
from ...utils.http_utils import http_request


class Instance(object):
    @staticmethod
    def _list(auth, serviceid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}?edit_mode=false&service_id={}".format(security, address,
                                                               "/dispatch/platform/v1/micro_services", serviceid)
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
    def _show(auth, instanceid):
        """查询单个实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/instances", instanceid)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        try:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            return data
        except Exception as e:
            raise

    @staticmethod
    def _deploy_batch(auth, serviceid, microserviceid, instanceids):
        """部署实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/instances/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=instanceids,
                                       micro_service_id=microserviceid,
                                       service_id=serviceid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"实例 {} 部署指令发送成功".format(','.join(instanceids)))
            print (u'Send "deploy {}" successfully'.format(','.join(instanceids)))
            return data.get("job_id", "")
        except Exception as e:
            raise

    @staticmethod
    def _undeploy_batch(auth, serviceid, microserviceid, instanceids):
        """卸载实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/instances/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=instanceids,
                                       micro_service_id=microserviceid,
                                       service_id=serviceid,
                                       delete_data=False))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"实例 {} 卸载指令发送成功".format(','.join(instanceids)))
            print (u'Send "undeploy {}" successfully'.format(','.join(instanceids)))
            return data.get("job_id", "")
        except Exception as e:
            raise

    @staticmethod
    def _delete_batch(auth, serviceid, microserviceid, instanceids):
        """批量删除实例"""
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/instances")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=instanceids,
                                       micro_service_id=microserviceid,
                                       service_id=serviceid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print (u"Delete instance {} complete".format(','.join(instanceids)))
        except Exception as e:
            raise

    @staticmethod
    def _add_batch(auth, serviceid, microserviceid, instanceids):
        """批量添加实例"""
        print(u"Developing")

    @staticmethod
    def _log(auth, instanceid):
        """实例日志"""
        short_auth_token, short_access_authority_token = auth.get_short_token()
        data = Instance._show(auth, instanceid)
        domain_name_service = data.get("domain_name_service", "")
        if not domain_name_service:
            raise Exception("Unknown Error")
        wsurl = "http://{}/webtty/{}:59998/{}/{}/?ins_id={}".format(auth.address, domain_name_service, short_auth_token,
                                                             short_access_authority_token, instanceid)
        try:
            cmd = "{} {}".format(auth.ttyclient, wsurl)
            os.system(cmd)
        except KeyboardInterrupt:
            exit(0)
        except Exception:
            raise

    @staticmethod
    def _terminal(auth, instanceid):
        """实例终端"""
        short_auth_token, short_access_authority_token = auth.get_short_token()
        data = Instance._show(auth, instanceid)
        domain_name_service = data.get("domain_name_service", "")
        if not domain_name_service:
            raise Exception("Unknown Error")
        wsurl = "http://{}/webtty/{}:59999/{}/{}/?ins_id={}".format(auth.address, domain_name_service, short_auth_token,
                                                                   short_access_authority_token, instanceid)
        try:
            cmd = "{} {}".format(auth.ttyclient, wsurl)
            os.system(cmd)
        except KeyboardInterrupt:
            exit(0)
        except Exception:
            raise
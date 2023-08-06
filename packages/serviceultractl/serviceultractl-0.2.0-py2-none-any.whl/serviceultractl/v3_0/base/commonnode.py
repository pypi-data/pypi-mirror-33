# -*- coding: utf-8 -*-
import json
from ...utils.http_utils import http_request


class CommonNode(object):
    @staticmethod
    def _list(auth):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/common_nodes")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        status, response_data = http_request(url=url, http_method=http_method, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        return data

    @staticmethod
    def _show(auth, machineid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        machineid = [machineid]
        url = "{}://{}{}{}".format(security, address, "/dispatch/platform/v1/common_nodes?ids=", ",".join(machineid))
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
    def _list_by_clusterid(auth, clusterid):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url1 = "{}://{}{}?cluster_id={}".format(security, address, "/dispatch/platform/v1/nodes", clusterid)
        url2 = "{}://{}{}?cluster_id={}".format(security, address, "/dispatch/nodemonitor/v1/nodes", clusterid)
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
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/statistics?type=common_node")
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token, "Content-Type": "application/json"}
        status, response_data = http_request(url=url, http_method=http_method, headers=headers)
        data = json.loads(response_data)
        if status != 200:
            message = data.get("message", "Unknown Error")
            raise Exception(message)
        return data

    @staticmethod
    def _deploy_batch(auth, clusterid, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes/deploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids,
                                       cluster_id=clusterid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"主机 {} 上线命令发送成功".format(','.join(machineids)))
            print (u'Send "deploy {}" successfully'.format(','.join(machineids)))
            return data.get("job_id", "")
        except Exception as e:
            raise

    @staticmethod
    def _undeploy_batch(auth, clusterid, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes/undeploy")
        http_method = "PUT"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids,
                                       cluster_id=clusterid,
                                       delete_data=True))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"主机 {} 下线命令发送成功".format(','.join(machineids)))
            print (u'Send "undeploy {}" successfully'.format(','.join(machineids)))
            return data.get("job_id", "")
        except Exception as e:
            raise

    @staticmethod
    def _delete_batch(auth, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/common_nodes")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"主机 {} 删除成功".format(','.join(machineids)))
            print (u"Delete machine {} complete".format(','.join(machineids)))
        except Exception as e:
            raise

    @staticmethod
    def _add_batch(auth, clusterid, machineids, virtual_node_num):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes")
        http_method = "POST"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(cluster_id=clusterid,
                                       common_nodes=
                                       [dict(common_node_id=machineid,
                                             virtual_node_num=virtual_node_num) for machineid in machineids]
                                       ))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"添加主机 {} 到集群 {} 成功".format(','.join(machineids), clusterid))
            print (u"Add machine {} to cluster {} complete".format(','.join(machineids), clusterid))
        except Exception as e:
            raise

    @staticmethod
    def _remove_batch(auth, clusterid, machineids):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}".format(security, address, "/dispatch/platform/v1/nodes")
        http_method = "DELETE"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        request_body = json.dumps(dict(ids=machineids,
                                       cluster_id=clusterid))
        try:
            status, response_data = http_request(url=url, http_method=http_method, body=request_body, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            # print (u"从集群 {} 移除主机 {} 成功".format(clusterid, ','.join(machineids)))
            print (u"Remove machine {} from cluster {} complete".format(','.join(machineids), clusterid))
        except Exception as e:
            raise












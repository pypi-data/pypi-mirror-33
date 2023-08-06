# -*- coding: utf-8 -*-
import json
import time
from ...utils.http_utils import http_request


class Common(object):
    @staticmethod
    def _job_check(timeout, auth, job_id):
        auth_token = auth.auth_token
        access_authority_token = auth.access_authority_token
        address = auth.address
        security = auth.security
        url = "{}://{}{}/{}".format(security, address, "/dispatch/platform/v1/jobs", job_id)
        http_method = "GET"
        headers = {"Authorization": auth_token, "X-Access-Authority": access_authority_token,
                   "Content-Type": "application/json"}
        deadline = int(time.time()) + timeout
        while int(time.time()) < deadline:
            status, response_data = http_request(url=url, http_method=http_method, headers=headers)
            data = json.loads(response_data)
            if status != 200:
                message = data.get("message", "Unknown Error")
                raise Exception(message)
            print "total step:{}, current step:{}.".format(data.get("total_step", ""), data.get("step", ""))
            if data.get("status", None):
                return data.get("status")
            time.sleep(5)
        raise Exception("timeout")

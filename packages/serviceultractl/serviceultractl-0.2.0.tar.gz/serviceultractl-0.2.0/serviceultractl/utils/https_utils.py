# -*- coding: utf-8 -*-
import socket
import requests

origin_socket = socket.socket


def https_request(url, https_method, body=None, json=None, headers=None, verify=True, auth=None, proxy_info=None, timeout=60):
    proxies = None
    socket.socket = origin_socket
    if proxy_info:
        username = proxy_info.get("socks_proxy_username")
        password = proxy_info.get("socks_proxy_password")
        ip = proxy_info.get("proxy_ip")
        port = proxy_info.get("socks_proxy_port")

        proxy_info_str = "socks5://{}:{}@{}:{}".format(username, password, ip, port)
        proxies = {
            'http': proxy_info_str,
            'https': proxy_info_str
        }
    try:
        if https_method == "POST":
            res = requests.post(url, body, json, headers=headers, verify=verify, auth=auth, proxies=proxies, timeout=timeout)
        elif https_method == "GET":
            res = requests.get(url, headers=headers, verify=verify, auth=auth, proxies=proxies, timeout=timeout)
        elif https_method == "DELETE":
            res = requests.delete(url, headers=headers, verify=verify, auth=auth, proxies=proxies, timeout=timeout)
        elif https_method == "PATCH":
            res = requests.patch(url, body, headers=headers, verify=verify, auth=auth, proxies=proxies, timeout=timeout)
        elif https_method == "HEAD":
            res = requests.head(url, headers=headers, verify=verify, auth=auth, proxies=proxies, timeout=timeout)
        elif https_method == "PUT":
            res = requests.put(url, data=body, verify=verify, auth=auth, proxies=proxies, timeout=timeout)
        else:
            raise Exception("unsupported https method: {}".format(https_method))
        return res.status_code, res.text
    except Exception as e:
        raise Exception("https error, can't connect to https server url: {}, proxy_info: {}, error_info: {}".format(url, proxy_info, e.message))



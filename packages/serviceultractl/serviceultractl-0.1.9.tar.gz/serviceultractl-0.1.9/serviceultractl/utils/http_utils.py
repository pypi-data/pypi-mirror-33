# -*- coding: utf-8 -*-


import socket
import requests

origin_socket = socket.socket


def http_request(url, http_method, body=None, json=None, headers=None, proxy_info=None, timeout=60):
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
        if http_method == "POST":
            res = requests.post(url, body, json, headers=headers, proxies=proxies, timeout=timeout)
        elif http_method == "GET":
            res = requests.get(url, headers=headers, proxies=proxies, timeout=timeout)
        elif http_method == "DELETE":
            res = requests.delete(url, data=body, headers=headers, proxies=proxies, timeout=timeout)
        elif http_method == "PATCH":
            res = requests.patch(url, body, headers=headers, proxies=proxies, timeout=timeout)
        elif http_method == "HEAD":
            res = requests.head(url, headers=headers, proxies=proxies, timeout=timeout)
        elif http_method == "PUT":
            res = requests.put(url, data=body, headers=headers, proxies=proxies, timeout=timeout)
        else:
            raise Exception("unsupported http method: {}".format(http_method))
        return res.status_code, res.text
    except Exception as e:
        raise Exception("http error, can't connect to http server url: {}, proxy_info: {}, error_info: {}".format(url, proxy_info, e.message))

# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     github_json.py
   Description :   GitHub JSON格式代理源
   Author :        JHao
   date：          2026/09/03
-------------------------------------------------
   Change Activity:
                   2026/09/03:
-------------------------------------------------
"""
__author__ = 'JHao'

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class GithubJsonFetcher(BaseFetcher):
    """CharlesPikachu/freeproxy JSON代理列表"""

    name = "github_json"
    url = "https://github.com/CharlesPikachu/freeproxy"

    # JSON格式代理列表地址, 结构: {"data": [{"ip": "", "port": 0, "protocol": "Http", ...}]}
    # 仅提取 protocol 为 Http 的代理(Socks 代理无法通过本池校验)
    # gh.mybacc.com 为 GitHub raw 加速代理, 直连可换成 raw.githubusercontent.com
    url_list = [
        "https://gh.mybacc.com/https://raw.githubusercontent.com/CharlesPikachu/freeproxy/master/proxies.json",
    ]

    def fetch(self):
        proxies = []
        for url in self.url_list:
            data = WebRequest().get(url, timeout=15).json
            for each in data.get("data", []):
                if str(each.get("protocol", "")).lower() != "http":
                    continue
                ip = str(each.get("ip", "")).strip()
                port = str(each.get("port", "")).strip()
                if ip and port:
                    proxies.append("%s:%s" % (ip, port))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in GithubJsonFetcher().fetch():
        print(proxy)

# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     github_list.py
   Description :   GitHub纯文本列表代理源
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


class GithubListFetcher(BaseFetcher):
    """GitHub纯文本代理列表 如 TheSpeedX/SOCKS-List"""

    name = "github_list"
    url = "https://github.com/TheSpeedX/SOCKS-List"

    # 纯文本代理列表地址(每行一个 ip:port), 支持添加多个同类列表
    # gh.mybacc.com 为 GitHub raw 加速代理, 直连可换成 raw.githubusercontent.com
    url_list = [
        "https://gh.mybacc.com/https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        # monosans/proxy-list (每10分钟更新)
        "https://gh.mybacc.com/https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        # clarketm/proxy-list (聚合多个来源的合并列表)
        "https://gh.mybacc.com/https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    ]

    def fetch(self):
        proxies = []
        for url in self.url_list:
            text = WebRequest().get(url, timeout=10).text
            proxies.extend(self.parseProxiesFromText(text))
        for proxy in self.yieldUniqueProxies(proxies):
            yield proxy


if __name__ == '__main__':
    for proxy in GithubListFetcher().fetch():
        print(proxy)

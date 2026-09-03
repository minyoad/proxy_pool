# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxydb.py
   Description :   proxydb.net 代理源
   Author :
   date：          2026/09/03
-------------------------------------------------
   Change Activity:
                   2026/09/03:
-------------------------------------------------
"""
__author__ = ''

import re
from time import sleep

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class ProxydbFetcher(BaseFetcher):
    """proxydb.net https://proxydb.net"""

    name = "proxydb"
    url = "https://proxydb.net"
    # href 格式: /ip/port#protocol  或  about:/ip/port#protocol
    _href_pattern = re.compile(r'(\d{1,3}(?:\.\d{1,3}){3})/(\d{2,5})')

    def fetch(self, page_count=5):
        for page in range(1, page_count + 1):
            url = "%s/?protocol=http&page=%d" % (self.url, page)
            tree = WebRequest().get(url, timeout=15).tree
            rows = tree.xpath('.//table//tr')
            for tr in rows[1:]:
                hrefs = tr.xpath('./td[1]//a/@href')
                for href in hrefs:
                    m = self._href_pattern.search(href)
                    if m:
                        yield "%s:%s" % (m.group(1), m.group(2))
                        break
            sleep(1)


if __name__ == '__main__':
    for proxy in ProxydbFetcher().fetch():
        print(proxy)

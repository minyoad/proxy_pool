# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_fetcher_sources.py
   Description :   各代理源 fetcher 测试
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from unittest.mock import patch, MagicMock

from lxml import etree

from fetcher.baseFetcher import BaseFetcher


# --------------- 辅助工具 ---------------

def _make_response(text="", tree=None, json_data=None):
    """构造 mock 的 WebRequest 返回对象"""
    resp = MagicMock()
    resp.text = text
    resp.tree = tree
    resp.json = json_data if json_data is not None else {}
    return resp


def _html_table(rows, has_header=False):
    """快速生成 HTML table 字符串"""
    html = "<table>"
    if has_header:
        html += "<tr><th>IP</th><th>Port</th></tr>"
    for ip, port in rows:
        html += "<tr><td>%s</td><td>%s</td></tr>" % (ip, port)
    html += "</table>"
    return html


def _assert_valid_proxies(proxies):
    """验证所有 proxy 符合 ip:port 格式"""
    pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$')
    for p in proxies:
        assert pattern.match(p), f"Invalid proxy format: {p}"


# --------------- 接口约定测试 ---------------

class TestFetcherInterface(object):
    """所有 fetcher 的接口约定"""

    FETCHER_CLASSES = [
        ("fetcher.sources.kxdaili", "KxdailiFetcher"),
        ("fetcher.sources.ip3366", "Ip3366Fetcher"),
        ("fetcher.sources.ip89", "Ip89Fetcher"),
        ("fetcher.sources.docip", "DocipFetcher"),
        ("fetcher.sources.goodips", "GoodipsFetcher"),
        ("fetcher.sources.geonode", "GeonodeFetcher"),

        ("fetcher.sources.kuaidaili", "KuaidailiFetcher"),
        ("fetcher.sources.freevpnnode", "FreeVPNNodeFetcher"),
        ("fetcher.sources.scdn", "ScdnFetcher"),
        ("fetcher.sources.zdaye", "ZdayeFetcher"),
        ("fetcher.sources.ihuan", "IhuanFetcher"),
        ("fetcher.sources.proxifly", "ProxiFlyFetcher"),
        ("fetcher.sources.daili66", "DaiLi66Fetcher"),
        ("fetcher.sources.roundproxies", "RoundProxiesFetcher"),
        ("fetcher.sources.github_list", "GithubListFetcher"),
        ("fetcher.sources.github_json", "GithubJsonFetcher"),
        ("fetcher.sources.proxydb", "ProxydbFetcher"),
    ]

    def test_all_fetchers_have_name_url_enabled(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert cls.name, f"{class_name} missing name"
            assert cls.url, f"{class_name} missing url"
            assert hasattr(cls, 'enabled'), f"{class_name} missing enabled"

    def test_all_fetchers_subclass_base(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert issubclass(cls, BaseFetcher), f"{class_name} not subclass of BaseFetcher"

    def test_all_fetchers_have_fetch_method(self):
        for module_path, class_name in self.FETCHER_CLASSES:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            assert hasattr(cls, 'fetch'), f"{class_name} missing fetch method"


# --------------- 各 fetcher 逻辑测试 ---------------

class TestKxdailiFetcher(object):

    @patch("fetcher.sources.kxdaili.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.kxdaili import KxdailiFetcher
        html = '<table class="active"><tr><th>IP</th><th>Port</th></tr>' \
               '<tr><td>1.2.3.4</td><td>8080</td></tr></table>'
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(KxdailiFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestIp3366Fetcher(object):

    @patch("fetcher.sources.ip3366.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.ip3366 import Ip3366Fetcher
        html = '<td>1.2.3.4</td><td>8080</td><td>5.6.7.8</td><td>3128</td>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(Ip3366Fetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result


class TestIp89Fetcher(object):

    @patch("fetcher.sources.ip89.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.ip89 import Ip89Fetcher
        html = '<td>1.2.3.4</td><td>8080</td>'
        mock_wr.return_value.get.return_value = _make_response(text=html)
        result = list(Ip89Fetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestDocipFetcher(object):

    @patch("fetcher.sources.docip.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.docip import DocipFetcher
        json_data = {"data": [{"ip": "1.2.3.4:8080"}, {"ip": "5.6.7.8:3128"}]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(DocipFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result


class TestGoodipsFetcher(object):

    @patch("fetcher.sources.goodips.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.goodips import GoodipsFetcher
        html = '<div class="table-list"><ul><li>1.2.3.4</li><li>8080</li></ul></div>'
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(GoodipsFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestGeonodeFetcher(object):

    @patch("fetcher.sources.geonode.WebRequest")
    def test_fetch_json(self, mock_wr):
        from fetcher.sources.geonode import GeonodeFetcher
        json_data = {"data": [{"ip": "1.2.3.4", "port": "8080"}]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GeonodeFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.geonode.WebRequest")
    def test_fetch_text_fallback(self, mock_wr):
        from fetcher.sources.geonode import GeonodeFetcher
        mock_wr.return_value.get.return_value = _make_response(
            json_data={}, text="1.2.3.4:8080")
        result = list(GeonodeFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestKuaidailiFetcher(object):

    @patch("fetcher.sources.kuaidaili.WebRequest")
    @patch("fetcher.sources.kuaidaili.sleep", return_value=None)
    def test_fetch(self, mock_sleep, mock_wr):
        from fetcher.sources.kuaidaili import KuaidailiFetcher
        # kuaidaili 使用 proxy_list[1:] 跳过第一行
        html = _html_table([("IP", "Port"), ("1.2.3.4", "8080")])
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(KuaidailiFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestFreeVPNNodeFetcher(object):

    @patch("fetcher.sources.freevpnnode.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.freevpnnode import FreeVPNNodeFetcher
        html = _html_table([("1.2.3.4", "8080")])
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(
            tree=tree, text="1.2.3.4:8080 5.6.7.8:3128")
        result = list(FreeVPNNodeFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result


class TestScdnFetcher(object):

    @patch("fetcher.sources.scdn.WebRequest")
    def test_fetch_json(self, mock_wr):
        from fetcher.sources.scdn import ScdnFetcher
        json_data = {"data": [{"ip": "1.2.3.4", "port": "8080"}]}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ScdnFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.scdn.WebRequest")
    def test_fetch_table_html(self, mock_wr):
        from fetcher.sources.scdn import ScdnFetcher
        table_html = '<tr><td>1.2.3.4</td><td>8080</td></tr>'
        json_data = {"table_html": table_html}
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ScdnFetcher().fetch())
        assert "1.2.3.4:8080" in result


class TestZdayeFetcher(object):

    @patch("fetcher.sources.zdaye.WebRequest")
    @patch("fetcher.sources.zdaye.sleep", return_value=None)
    @patch("fetcher.sources.zdaye.datetime")
    def test_fetch_recent(self, mock_dt, mock_sleep, mock_wr):
        from fetcher.sources.zdaye import ZdayeFetcher
        from datetime import datetime as real_datetime
        # 模拟最新帖子时间在5分钟内
        mock_dt.now.return_value = real_datetime(2026, 5, 31, 12, 0, 0)
        mock_dt.strptime.return_value = real_datetime(2026, 5, 31, 11, 58, 0)

        index_tree = etree.HTML(
            '<span class="thread_time_info">2026/05/31 11:58:00</span>'
            '<h3 class="thread_title"><a href="/detail/1">test</a></h3>')
        detail_tree = etree.HTML(_html_table([("1.2.3.4", "8080")]))

        def side_effect(url, **kwargs):
            resp = MagicMock()
            if "free" in url:
                resp.tree = index_tree
            else:
                resp.tree = detail_tree
            return resp

        mock_wr.return_value.get.side_effect = side_effect
        result = list(ZdayeFetcher().fetch())
        assert "1.2.3.4:8080" in result

    @patch("fetcher.sources.zdaye.WebRequest")
    @patch("fetcher.sources.zdaye.datetime")
    def test_fetch_old_returns_empty(self, mock_dt, mock_wr):
        from fetcher.sources.zdaye import ZdayeFetcher
        from datetime import datetime as real_datetime
        # 模拟最新帖子时间超过5分钟
        mock_dt.now.return_value = real_datetime(2026, 5, 31, 12, 0, 0)
        mock_dt.strptime.return_value = real_datetime(2026, 5, 31, 10, 0, 0)

        index_tree = etree.HTML(
            '<span class="thread_time_info">2026/05/31 10:00:00</span>'
            '<h3 class="thread_title"><a href="/detail/1">test</a></h3>')
        mock_wr.return_value.get.return_value = _make_response(tree=index_tree)
        result = list(ZdayeFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.zdaye.WebRequest")
    @patch("fetcher.sources.zdaye.datetime")
    def test_fetch_old_cross_day_returns_empty(self, mock_dt, mock_wr):
        """跨天帖子应判定为过期（total_seconds 而非 seconds）"""
        from fetcher.sources.zdaye import ZdayeFetcher
        from datetime import datetime as real_datetime
        # 帖子是昨天 23:59，当前是今天 00:01（差 2 分钟，但跨天）
        mock_dt.now.return_value = real_datetime(2026, 5, 31, 0, 1, 0)
        mock_dt.strptime.return_value = real_datetime(2026, 5, 30, 23, 59, 0)

        index_tree = etree.HTML(
            '<span class="thread_time_info">2026/05/30 23:59:00</span>'
            '<h3 class="thread_title"><a href="/detail/1">test</a></h3>')
        mock_wr.return_value.get.return_value = _make_response(tree=index_tree)
        result = list(ZdayeFetcher().fetch())
        assert result == []


class TestIhuanFetcher(object):

    @patch("fetcher.sources.ihuan.requests")
    def test_fetch(self, mock_requests):
        from fetcher.sources.ihuan import IhuanFetcher
        html = (
            '<table class="table table-hover table-bordered">'
            '<tr><td>1.2.3.4</td><td>8080</td></tr>'
            '<tr><td>5.6.7.8</td><td>3128</td></tr>'
            '</table>'
        )
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = html
        # 第一次 get 获取 cookie，第二次 get 返回数据
        mock_session.get.return_value = mock_resp
        mock_requests.session.return_value = mock_session

        result = list(IhuanFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert mock_session.get.call_count == 2

    @patch("fetcher.sources.ihuan.requests")
    def test_fetch_empty_table_returns_empty(self, mock_requests):
        from fetcher.sources.ihuan import IhuanFetcher
        html = '<table class="table table-hover table-bordered"></table>'
        mock_session = MagicMock()
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_session.get.return_value = mock_resp
        mock_requests.session.return_value = mock_session

        result = list(IhuanFetcher().fetch())
        assert result == []


class TestProxiFlyFetcher(object):

    @patch("fetcher.sources.proxifly.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.proxifly import ProxiFlyFetcher
        json_data = [
            {"proxy": "1.2.3.4:8080", "protocol": "http", "geolocation": {"country": "CN"}},
            {"proxy": "5.6.7.8:3128", "protocol": "http", "geolocation": {"country": "CN"}},
        ]
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ProxiFlyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxifly.WebRequest")
    def test_fetch_filters_non_cn(self, mock_wr):
        from fetcher.sources.proxifly import ProxiFlyFetcher
        json_data = [
            {"proxy": "1.2.3.4:8080", "protocol": "http", "geolocation": {"country": "CN"}},
            {"proxy": "9.9.9.9:8080", "protocol": "http", "geolocation": {"country": "US"}},
        ]
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ProxiFlyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "9.9.9.9:8080" not in result

    @patch("fetcher.sources.proxifly.WebRequest")
    def test_fetch_filters_non_http(self, mock_wr):
        from fetcher.sources.proxifly import ProxiFlyFetcher
        json_data = [
            {"proxy": "1.2.3.4:8080", "protocol": "http", "geolocation": {"country": "CN"}},
            {"proxy": "9.9.9.9:8080", "protocol": "https", "geolocation": {"country": "CN"}},
        ]
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(ProxiFlyFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "9.9.9.9:8080" not in result


class TestDaiLi66Fetcher(object):

    @patch("fetcher.sources.daili66.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.daili66 import DaiLi66Fetcher
        json_data = {
            "data": [
                {"ip": "1.2.3.4", "port": "8080"},
                {"ip": "5.6.7.8", "port": "3128"},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(DaiLi66Fetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.daili66.WebRequest")
    def test_fetch_empty_data_returns_empty(self, mock_wr):
        from fetcher.sources.daili66 import DaiLi66Fetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        result = list(DaiLi66Fetcher().fetch())
        assert result == []


class TestRoundProxiesFetcher(object):

    @patch("fetcher.sources.roundproxies.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.roundproxies import RoundProxiesFetcher
        json_data = {
            "data": [
                {"ip": "1.2.3.4", "port": "8080"},
                {"ip": "5.6.7.8", "port": "3128"},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(RoundProxiesFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.roundproxies.WebRequest")
    def test_fetch_empty_data_returns_empty(self, mock_wr):
        from fetcher.sources.roundproxies import RoundProxiesFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        result = list(RoundProxiesFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.roundproxies.WebRequest")
    def test_fetch_exception_returns_empty(self, mock_wr):
        from fetcher.sources.roundproxies import RoundProxiesFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data=None)
        result = list(RoundProxiesFetcher().fetch())
        assert result == []


class TestGithubListFetcher(object):

    @patch("fetcher.sources.github_list.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.github_list import GithubListFetcher
        text = "1.2.3.4:8080\n5.6.7.8:3128\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(GithubListFetcher().fetch())
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.github_list.WebRequest")
    def test_fetch_multiple_urls_merged(self, mock_wr):
        """多个列表合并, 请求次数与 url_list 一致"""
        from fetcher.sources.github_list import GithubListFetcher

        def side_effect(url, **kwargs):
            texts = {
                "TheSpeedX": "1.1.1.1:80\n",
                "monosans": "2.2.2.2:80\n",
                "clarketm": "3.3.3.3:80\n",
            }
            for key, text in texts.items():
                if key in url:
                    return _make_response(text=text)
            return _make_response(text="")

        mock_wr.return_value.get.side_effect = side_effect
        result = list(GithubListFetcher().fetch())
        assert sorted(result) == ["1.1.1.1:80", "2.2.2.2:80", "3.3.3.3:80"]
        assert mock_wr.return_value.get.call_count == len(GithubListFetcher.url_list)

    @patch("fetcher.sources.github_list.WebRequest")
    def test_fetch_deduplicates_across_lists(self, mock_wr):
        """跨列表重复代理去重"""
        from fetcher.sources.github_list import GithubListFetcher

        def side_effect(url, **kwargs):
            text = "1.2.3.4:8080\n" if "TheSpeedX" in url else \
                  ("1.2.3.4:8080\n5.6.7.8:3128\n" if "monosans" in url else "")
            return _make_response(text=text)

        mock_wr.return_value.get.side_effect = side_effect
        result = list(GithubListFetcher().fetch())
        assert sorted(result) == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.github_list.WebRequest")
    def test_fetch_empty_text_returns_empty(self, mock_wr):
        from fetcher.sources.github_list import GithubListFetcher
        mock_wr.return_value.get.return_value = _make_response(text="")
        result = list(GithubListFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.github_list.WebRequest")
    def test_fetch_ignores_invalid_lines(self, mock_wr):
        """非 ip:port 行被忽略"""
        from fetcher.sources.github_list import GithubListFetcher
        text = "1.2.3.4:8080\nnot a proxy\n# comment\n1.2.3.4:8\n5.6.7.8:3128\n"
        mock_wr.return_value.get.return_value = _make_response(text=text)
        result = list(GithubListFetcher().fetch())
        assert sorted(result) == ["1.2.3.4:8080", "5.6.7.8:3128"]


class TestProxydbFetcher(object):

    @patch("fetcher.sources.proxydb.WebRequest")
    @patch("fetcher.sources.proxydb.sleep", return_value=None)
    def test_fetch(self, mock_sleep, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        html = (
            '<table><tr><th>IP</th><th>Port</th></tr>'
            '<tr><td><a href="/1.2.3.4/8080#http">1.2.3.4</a></td>'
            '<td><a href="/1.2.3.4/8080#http">8080</a></td></tr>'
            '<tr><td><a href="/5.6.7.8/3128#http">5.6.7.8</a></td>'
            '<td><a href="/5.6.7.8/3128#http">3128</a></td></tr>'
            '</table>'
        )
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(ProxydbFetcher().fetch(page_count=1))
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result

    @patch("fetcher.sources.proxydb.WebRequest")
    @patch("fetcher.sources.proxydb.sleep", return_value=None)
    def test_fetch_skips_invalid_rows(self, mock_sleep, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        html = (
            '<table><tr><th>IP</th><th>Port</th></tr>'
            '<tr><td><a href="/1.2.3.4/8080#http">1.2.3.4</a></td></tr>'
            '<tr><td>no link here</td></tr>'
            '<tr><td><a href="/not-a-proxy">bad</a></td></tr>'
            '</table>'
        )
        tree = etree.HTML(html)
        mock_wr.return_value.get.return_value = _make_response(tree=tree)
        result = list(ProxydbFetcher().fetch(page_count=1))
        assert result == ["1.2.3.4:8080"]

    @patch("fetcher.sources.proxydb.WebRequest")
    @patch("fetcher.sources.proxydb.sleep", return_value=None)
    def test_fetch_multi_page(self, mock_sleep, mock_wr):
        from fetcher.sources.proxydb import ProxydbFetcher
        page1 = '<table><tr><th>IP</th><th>Port</th></tr>' \
                '<tr><td><a href="/1.2.3.4/8080#http">1.2.3.4</a></td></tr></table>'
        page2 = '<table><tr><th>IP</th><th>Port</th></tr>' \
                '<tr><td><a href="/5.6.7.8/3128#http">5.6.7.8</a></td></tr></table>'
        mock_wr.return_value.get.side_effect = [
            _make_response(tree=etree.HTML(page1)),
            _make_response(tree=etree.HTML(page2)),
        ]
        result = list(ProxydbFetcher().fetch(page_count=2))
        assert "1.2.3.4:8080" in result
        assert "5.6.7.8:3128" in result
        assert mock_wr.return_value.get.call_count == 2


class TestGithubJsonFetcher(object):

    @patch("fetcher.sources.github_json.WebRequest")
    def test_fetch(self, mock_wr):
        from fetcher.sources.github_json import GithubJsonFetcher
        json_data = {
            "updated_at": "2026-09-03 03:53:02 UTC",
            "count": 2,
            "data": [
                {"ip": "1.2.3.4", "port": 8080, "protocol": "Http",
                 "country": "KH", "anonymity": "Elite", "speed": 1007},
                {"ip": "5.6.7.8", "port": 3128, "protocol": "Http",
                 "country": "CN", "anonymity": "Elite", "speed": 1092},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GithubJsonFetcher().fetch())
        assert sorted(result) == ["1.2.3.4:8080", "5.6.7.8:3128"]

    @patch("fetcher.sources.github_json.WebRequest")
    def test_fetch_filters_socks(self, mock_wr):
        """Socks4/Socks5 代理被过滤"""
        from fetcher.sources.github_json import GithubJsonFetcher
        json_data = {
            "data": [
                {"ip": "1.2.3.4", "port": 8080, "protocol": "Http"},
                {"ip": "5.6.7.8", "port": 1080, "protocol": "Socks4"},
                {"ip": "9.9.9.9", "port": 1080, "protocol": "Socks5"},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GithubJsonFetcher().fetch())
        assert result == ["1.2.3.4:8080"]

    @patch("fetcher.sources.github_json.WebRequest")
    def test_fetch_empty_data_returns_empty(self, mock_wr):
        from fetcher.sources.github_json import GithubJsonFetcher
        mock_wr.return_value.get.return_value = _make_response(json_data={})
        result = list(GithubJsonFetcher().fetch())
        assert result == []

    @patch("fetcher.sources.github_json.WebRequest")
    def test_fetch_skips_missing_ip_or_port(self, mock_wr):
        """缺 ip 或 port 的条目被跳过"""
        from fetcher.sources.github_json import GithubJsonFetcher
        json_data = {
            "data": [
                {"ip": "1.2.3.4", "port": 8080, "protocol": "Http"},
                {"port": 3128, "protocol": "Http"},
                {"ip": "5.6.7.8", "protocol": "Http"},
                {"ip": "", "port": 80, "protocol": "Http"},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GithubJsonFetcher().fetch())
        assert result == ["1.2.3.4:8080"]

    @patch("fetcher.sources.github_json.WebRequest")
    def test_fetch_deduplicates(self, mock_wr):
        """重复代理去重"""
        from fetcher.sources.github_json import GithubJsonFetcher
        json_data = {
            "data": [
                {"ip": "1.2.3.4", "port": 8080, "protocol": "Http"},
                {"ip": "1.2.3.4", "port": 8080, "protocol": "Http"},
                {"ip": "5.6.7.8", "port": 3128, "protocol": "Http"},
            ]
        }
        mock_wr.return_value.get.return_value = _make_response(json_data=json_data)
        result = list(GithubJsonFetcher().fetch())
        assert sorted(result) == ["1.2.3.4:8080", "5.6.7.8:3128"]

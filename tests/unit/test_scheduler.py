# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_scheduler.py
   Description :   helper/scheduler.py 单元测试
   Author :        JHao
   date：          2026/6/15
-------------------------------------------------
     Change Activity:
                     2026/06/15:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
import pytest
from unittest.mock import patch, MagicMock


# apscheduler 依赖 pkg_resources，在 tox/uv 环境中可能缺失
# 在 import 前 mock 掉，避免 collection 阶段报错
_apscheduler_mock = MagicMock()
sys.modules.setdefault("apscheduler", _apscheduler_mock)
sys.modules.setdefault("apscheduler.schedulers", _apscheduler_mock.schedulers)
sys.modules.setdefault("apscheduler.schedulers.blocking", _apscheduler_mock.schedulers.blocking)
sys.modules.setdefault("apscheduler.executors", _apscheduler_mock.executors)
sys.modules.setdefault("apscheduler.executors.pool", _apscheduler_mock.executors.pool)

import helper.scheduler as scheduler_mod


def _get_attr(name):
    """获取模块中双下划线开头的属性（绕过类内 name mangling）"""
    return getattr(scheduler_mod, name)


class TestRunProxyFetch:

    @patch("helper.scheduler.Checker")
    @patch("helper.scheduler.Fetcher")
    @patch("helper.scheduler.ProxyHandler")
    def test_fetcher_yields_go_to_queue(self, mock_ph_cls, mock_fetcher_cls, mock_checker):
        """Fetcher yield 的新代理放入 queue，传给 Checker"""
        mock_proxy = MagicMock()
        mock_proxy.proxy = "1.2.3.4:8080"
        mock_fetcher = MagicMock()
        mock_fetcher.run.return_value = iter([mock_proxy])
        mock_fetcher_cls.return_value = mock_fetcher

        mock_ph = MagicMock()
        mock_ph.getAll.return_value = []
        mock_ph_cls.return_value = mock_ph

        _get_attr("__runProxyFetch")()

        mock_fetcher_cls.assert_called_once()
        mock_checker.assert_called_once()
        call_args = mock_checker.call_args
        assert call_args[0][0] == "raw"
        queue = call_args[0][1]
        assert queue.get(block=False) is mock_proxy

    @patch("helper.scheduler.Checker")
    @patch("helper.scheduler.Fetcher")
    @patch("helper.scheduler.ProxyHandler")
    def test_existing_proxies_skipped(self, mock_ph_cls, mock_fetcher_cls, mock_checker):
        """已入库代理跳过raw校验, 不进 queue"""
        new_proxy = MagicMock()
        new_proxy.proxy = "1.1.1.1:80"
        old_proxy = MagicMock()
        old_proxy.proxy = "2.2.2.2:80"
        mock_fetcher = MagicMock()
        mock_fetcher.run.return_value = iter([old_proxy, new_proxy])
        mock_fetcher_cls.return_value = mock_fetcher

        existing = MagicMock()
        existing.proxy = "2.2.2.2:80"
        mock_ph = MagicMock()
        mock_ph.getAll.return_value = [existing]
        mock_ph_cls.return_value = mock_ph

        _get_attr("__runProxyFetch")()

        queue = mock_checker.call_args[0][1]
        assert queue.qsize() == 1
        assert queue.get(block=False) is new_proxy


class TestRunProxyCheck:

    @patch("helper.scheduler.Checker")
    @patch("helper.scheduler.ProxyHandler")
    def test_all_proxies_go_to_use_check(self, mock_ph_cls, mock_checker):
        """getAll 的代理放入 queue，传给 use Checker"""
        mock_proxy = MagicMock()
        mock_ph = MagicMock()
        mock_ph.getAll.return_value = [mock_proxy]
        mock_ph_cls.return_value = mock_ph

        _get_attr("__runProxyCheck")()

        mock_checker.assert_called_once()
        call_args = mock_checker.call_args
        assert call_args[0][0] == "use"
        queue = call_args[0][1]
        assert queue.get(block=False) is mock_proxy


class TestRefresh:

    @patch("helper.scheduler.__runProxyCheck")
    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.ProxyHandler")
    def test_refresh_fetch_then_check(self, mock_ph_cls, mock_fetch, mock_check):
        """池子充足: fetch 一次后 check"""
        mock_ph = MagicMock()
        mock_ph.db.getCount.return_value = {"total": 50}
        mock_ph.conf.poolSizeMin = 20
        mock_ph_cls.return_value = mock_ph

        _get_attr("__refresh")()

        assert mock_fetch.call_count == 1
        mock_check.assert_called_once()

    @patch("helper.scheduler.__runProxyCheck")
    @patch("helper.scheduler.__runProxyFetch")
    @patch("helper.scheduler.ProxyHandler")
    def test_refresh_refetch_when_pool_low(self, mock_ph_cls, mock_fetch, mock_check):
        """池子低于 poolSizeMin: 补抓一次后再 check"""
        mock_ph = MagicMock()
        mock_ph.db.getCount.return_value = {"total": 5}
        mock_ph.conf.poolSizeMin = 20
        mock_ph_cls.return_value = mock_ph

        _get_attr("__refresh")()

        assert mock_fetch.call_count == 2
        mock_check.assert_called_once()


class TestRunScheduler:

    @patch("helper.scheduler.BlockingScheduler")
    @patch("helper.scheduler.__refresh")
    @patch("helper.scheduler.ConfigHandler")
    @patch("helper.scheduler.LogHandler")
    def test_adds_single_refresh_job(self, mock_log, mock_conf_cls, mock_refresh, mock_sched_cls):
        """runScheduler 只添加一个刷新定时任务(不再有独立的use检查任务)"""
        mock_conf = MagicMock()
        mock_conf.timezone = "Asia/Shanghai"
        mock_conf_cls.return_value = mock_conf
        mock_sched = MagicMock()
        mock_sched_cls.return_value = mock_sched

        scheduler_mod.runScheduler()

        assert mock_sched.add_job.call_count == 1
        # 启动时立即执行一次刷新
        mock_refresh.assert_called_once()

    @patch("helper.scheduler.BlockingScheduler")
    @patch("helper.scheduler.__refresh")
    @patch("helper.scheduler.ConfigHandler")
    @patch("helper.scheduler.LogHandler")
    def test_refresh_job_interval_30min(self, mock_log, mock_conf_cls, mock_refresh, mock_sched_cls):
        """刷新任务间隔 30 分钟"""
        mock_conf = MagicMock()
        mock_conf.timezone = "Asia/Shanghai"
        mock_conf_cls.return_value = mock_conf
        mock_sched = MagicMock()
        mock_sched_cls.return_value = mock_sched

        scheduler_mod.runScheduler()

        calls = mock_sched.add_job.call_args_list
        call = calls[0]
        assert call[0][1] == "interval"
        assert call[1]["minutes"] == 30
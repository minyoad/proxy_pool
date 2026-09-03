# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()
    proxy_handler = ProxyHandler()
    # 已入库代理跳过raw校验(已入库代理由use校验定期复查), 只校验新代理
    existing = set(_.proxy for _ in proxy_handler.getAll())

    new_count = 0
    for proxy in proxy_fetcher.run():
        if proxy.proxy in existing:
            continue
        new_count += 1
        proxy_queue.put(proxy)

    scheduler_log = LogHandler("scheduler")
    scheduler_log.info("ProxyFetch: %d new proxies to check" % new_count)
    Checker("raw", proxy_queue)


def __runProxyCheck():
    """use全量校验: 由__refresh在采集完成后触发, 不再独立定时执行"""
    proxy_handler = ProxyHandler()
    proxy_queue = Queue()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)


def __refresh():
    """刷新流程: 采集 -> (池子不足时补抓) -> use全量校验"""
    __runProxyFetch()
    proxy_handler = ProxyHandler()
    if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
        __runProxyFetch()
    __runProxyCheck()


def runScheduler():
    __refresh()

    timezone = ConfigHandler().timezone
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    scheduler.add_job(__refresh, 'interval', minutes=10, id="proxy_refresh", name="proxy刷新")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()

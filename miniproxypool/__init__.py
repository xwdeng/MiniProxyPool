#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.


from .random_useragent import UserAgent
from .proxypool import ProxyPool
from .restapi import start_rest_api_thread
import miniproxypool.config
import threading
import logging
proxypool_inst = None
t1 = None;
t2 = None;
t3 = None;
def run_as_daemon():
    global proxypool_inst
    if (proxypool_inst == None):
        proxypool_inst = ProxyPool()

    logging.warning("Mini Proxy Pool is running now...")
    if len(proxypool_inst._get_all_proxies()) == 0:
        logging.warning("First time running is detected. Please wait database to be initialized...")
        proxypool_inst._fetch_proxies_from_sites()
        proxypool_inst.run_validators()
    logging.warning("Database initializaion done.")

    global t1, t2
    t1 = threading.Thread(target=proxypool_inst.start_monitor_thread)
    t1.setDaemon(True)
    t2 = threading.Thread(target=proxypool_inst.start_load_from_sites_thread)
    t2.setDaemon(True)

    t1.start()
    t2.start()

def run_rest_api_serv():
    global proxypool_inst
    if (proxypool_inst == None):
        proxypool_inst = ProxyPool()
    global t3
    t3 = threading.Thread(target=start_rest_api_thread, args=(proxypool_inst,))
    t3.setDaemon(True)
    t3.start()


def get_all_proxies():
    global proxypool_inst
    if (proxypool_inst == None):
        proxypool_inst = ProxyPool()
    return proxypool_inst.get_valid_proxies()

def rest_api_url_get_all_valid_proxiex():
    return "http://" + "localhost:" + miniproxypool.config.REST_SRV_PORT + miniproxypool.config.REST_API_PATH_GET_ALL_VALID


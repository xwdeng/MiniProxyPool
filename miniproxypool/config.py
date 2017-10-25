#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.

PROXY_DB_FILE = "_proxies.db"

VALIDATOR_TIMEOUT = 1 # seconds
VALIDATOR_URL = "http://www.google.ca"
VALIDATOR_THREAD_POOL_SIZE = 20
VALIDATOR_CONNECTIONS_PER_THREAD = 20

INVALID_PROXY_TIMES = 5 # if a proxy cannot be connected for VALIDATOR_DEFINE_INVALID_TIMES time, it is defined as invalid
INVALID_PROXY_IF_DELETE = True

VALIDATE_THREAD_RUN_PERIOD = 5 # seconds wait after each validation
LOAD_FROM_SITES_THREAD_RUN_PERIOD = 30 * 60 # seconds wait after each loading from sites

REST_SRV_IP = "0.0.0.0"
REST_SRV_PORT = 9876

# Free proxy sites
PROXY_SITES = [
        {
            'url_base': "https://free-proxy-list.net",
            'pattern': "((?:\d{1,3}\.){1,3}\d{1,3})<\/td><td>(\d{1,6})(.{1,200})<td class='hx'>(.{2,3})",
            'ip_ind': 0,
            'port_ind': 1,
            'protocal_ind': 3
        },
        {
             'url_base': 'https://www.us-proxy.org',
             'pattern': "((?:\d{1,3}\.){1,3}\d{1,3})<\/td><td>(\d{1,6})(.{1,200})<td class='hx'>(.{2,3})",
             'ip_ind': 0,
             'port_ind': 1,
             'protocal_ind': 3  # todo: to specify the protocol: http or https
        },
        {
            'url_base': "http://spys.me/proxy.txt",
            'pattern': '((?:\d{1,3}\.){1,3}\d{1,3}):(\d{1,6})',
            'ip_ind': 0,
            'port_ind': 1,
            'protocal_ind': None
        }
]

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2693.2 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Accept-Encoding': 'gzip, default',
}

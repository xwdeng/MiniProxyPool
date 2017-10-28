#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.

from .proxydb import ProxyDB
from .validator import *
import miniproxypool.config
from .random_useragent import UserAgent
from multiprocessing.pool import ThreadPool
import logging
import re

logger = logging.getLogger(__name__)
ua = UserAgent()


class ProxyPool():
    def __init__(self):
        self.db = ProxyDB()
        self.db.init_dbconn(miniproxypool.config.PROXY_DB_FILE)
        self.db.create_table_proxy() ##create
        self._thread_pool = None
        logger.debug("ProxyPool init done.")
        #self._process_pool = Pool(VALIDATOR_THREAD_POOL_SIZE)

    def start_monitor_thread(self):
        if self._thread_pool == None:
            self._thread_pool = ThreadPool(miniproxypool.config.VALIDATOR_THREAD_POOL_SIZE)

        logger.warning("Mini Proxy Pool is running now...")
        logger.info("CONFIG: Validators runs in every %d minutes. VALIDATING URL: %s" % (
            int(miniproxypool.config.VALIDATE_THREAD_RUN_PERIOD / 60),
            miniproxypool.config.VALIDATOR_URL))
        if miniproxypool.config.INVALID_PROXY_IF_DELETE:
            logger.info("CONFIG: Invalid proxies will be cleared from DB.")

        while True:
            self.run_validators()
            if miniproxypool.config.INVALID_PROXY_IF_DELETE:
                self.clear_invalid_proxies()
            time.sleep(miniproxypool.config.VALIDATE_THREAD_RUN_PERIOD)

    def start_load_from_sites_thread(self):
        logger.info("CONFIG: Reading proxy-list from sites in every %d minutes" % int(miniproxypool.config.LOAD_FROM_SITES_THREAD_RUN_PERIOD/60))
        while(True):
            self._fetch_proxies_from_sites()
            time.sleep(miniproxypool.config.LOAD_FROM_SITES_THREAD_RUN_PERIOD)

    def _fetch_proxies_from_sites(self):
        """
        Load all the proxy entries from Sites configured in miniproxypool.config.py to Dababase.
        Only new entry (ip:port) would be imported.
        """
        logger.info("Loading proxy-entries from configured web-sites...")
        sites = miniproxypool.config.PROXY_SITES
        for site in sites:
            url_base = site['url_base']
            pattern = re.compile(site['pattern'])
            ip_ind = site['ip_ind']
            port_ind = site['port_ind']

            header = miniproxypool.config.DEFAULT_HEADERS
            header['User-agent'] = ua.random()
            try:
                r = requests.get(url_base, headers = header, timeout = 5)
                cnt_newproxy = 0
                for match in pattern.findall(r.text):
                    ip = match[ip_ind]
                    port = match[port_ind]

                    res = self.db.add_new_proxy(ip, port, 'http', -1) # speed = -1, means not tested yet
                    if res:
                        cnt_newproxy += 1
                logger.info("  Site [%s]: %d new proxies are added to DB."% (url_base, cnt_newproxy))
            except Exception as e:
                logger.info(e)
        logger.info("Loading all done. There're %d proxies in the DB."%len(self._get_all_proxies()))



    def get_valid_proxies(self):
        """
        Return all the proxy entries in the DB.
        :return:
            [(ip, port), (ip, port), ...]
        """
        return self.db.get_valid_proxies()

    def _get_all_proxies(self):
        return self.db.get_all_proxies()

    def _chunks(self, seq, n):
        """Split the seq into chunks. Each chunk has size of n"""
        return (seq[i:i + n] for i in range(0, len(seq), n))

    def run_validators(self):
        if self._thread_pool == None:
            self._thread_pool = ThreadPool(miniproxypool.config.VALIDATOR_THREAD_POOL_SIZE)

        proxyUrls = self._get_all_proxies()
        logger.info("Validators starts... (%d proxies in the DB)..."%len(proxyUrls))

        urlObjs = []
        for url in proxyUrls:
            headers = miniproxypool.config.DEFAULT_HEADERS
            headers['User-agent'] = ua.random()
            urlObjs.append(UrlObj(miniproxypool.config.VALIDATOR_URL, headers, "%s:%s" % (url[0], url[1]), url[2])) #"http://103.238.68.184:8888" ) ) #"

        split_urlObjs = self._chunks(urlObjs, miniproxypool.config.VALIDATOR_CONNECTIONS_PER_THREAD)


        urlObjs_groups = []
        for t in split_urlObjs:
            urlObjs_groups.append(t)

        # can either use validate_proxy_list_aiohttp() or validate_proxy_list_blocked()
        #ress = self._process_pool.map(validate_proxy_list_aiohttp, urlObjs_groups)
        ress = self._thread_pool.map(validate_proxy_list_blocked, urlObjs_groups)
        self._save_all_validator_results(ress)

        logger.info("Validators done!! (%d VALID proxies in the DB)" % len(self.get_valid_proxies()))

    def _save_all_validator_results(self, ress):
        logger.info("Saving results into DB....")
        proxies = []
        for res in ress:
            for valUrlRes in res:
                if isinstance(valUrlRes, UrlObj):
                    ip_port = valUrlRes.proxy.split(':')
                    proxy_entry = {
                        'ip': ip_port[0],
                        'port':  ip_port[1],
                        'protocol': "http",
                        'speed': valUrlRes.speed
                    }
                    proxies.append(proxy_entry)
        errs = self.db.update_proxies(proxies)
        logger.info("   %d proxies are updated." % len(proxies))
    
    def clear_invalid_proxies(self):
        self.db.delete_invalid_proxies()


proxypool_inst = ProxyPool()
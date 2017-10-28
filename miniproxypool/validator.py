#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.

import datetime
import random
import time
import logging
import miniproxypool.config
import requests
import multiprocessing

logger = logging.getLogger(__name__)
UNREACHABLE = 100


class UrlObj:
    """
    Corresponding to proxyDB record.
        ip, port, speed
    """
    def __init__(self, url, headers, proxy, speed):
        """
        Specify that the @url needs @speed time to reach miniproxypool.config.VALIDATOR_URL (requests header is @headers)
        :param url:  full url.  e.g. http://www.google.ca
        :param headers: dict.   e.g. {'User-Agent': 'Chrome....', ...}
        :param proxy: str.      e.g. "ip:port"
        :param speed: float.    e.g. 1.1
        """
        self.url = url
        self.headers = headers
        self.proxy = proxy
        self.speed = speed

    def __str__(self):
        return "%s" % (self.proxy)


def validate_proxy_list_blocked(url_objs):
    """
    Validate and update speed in each urlObj and return the updated urlObjs list.
    Note: this function validate the urlObjs by using requests.get() which is a blocked function.
    """
    url_objs_res = []
    for urb_obj in url_objs:
        try:
            proxies = {
                'http': 'http://' + urb_obj.proxy,
                'https': 'https://' + urb_obj.proxy,
            }
            start = time.time()
            res = requests.get(urb_obj.url, proxies=proxies,  timeout=miniproxypool.config.VALIDATOR_TIMEOUT)
            roundtrip = time.time() - start
            speed = 0;
            if res.status_code == 200:
                speed = roundtrip
                logger.debug("[%s]succeeded: validating [%25s] speed: %f" % (__name__, urb_obj.proxy, roundtrip))
            else:
                speed = UNREACHABLE
                logger.debug("failed: validating [%25s] status code: %f" % (urb_obj.proxy, res.status_code))
        except Exception as e:
            speed = UNREACHABLE
            logger.debug("failed: validating: [%25s] (%s)" % (urb_obj.proxy, type(e)))
        finally:
            if speed < UNREACHABLE:
                urb_obj.speed = speed
            else:
                urb_obj.speed += speed
            url_objs_res.append(urb_obj)
    return url_objs_res

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.

import asyncio
import aiohttp
import datetime
import random
import time
import logging
from .config import VALIDATOR_TIMEOUT
import requests
import multiprocessing

class UrlObj:
    def __init__(self, url, headers, proxy, speed):
        self.url = url
        self.headers = headers
        self.proxy = proxy
        self.speed = speed

    def __str__(self):
        return "%s"%(self.proxy)

UNREACHABLE = 100
def validate_proxy_list_blocked(urlObjs):
    urlObjs_res = []
    for urlObj in urlObjs:
        try:
            proxies = {
                'http': 'http://' + urlObj.proxy,
                'https': 'https://' + urlObj.proxy,
            }
            start = time.time()
            res = requests.get(urlObj.url, proxies = proxies,  timeout = VALIDATOR_TIMEOUT)
            roundtrip = time.time() - start
            speed = 0;
            if res.status_code == 200:
                speed = roundtrip
                logging.debug("succeeded: validating: %s. speed: %f" % (urlObj.proxy, roundtrip))
            else:
                speed = UNREACHABLE
                logging.debug("failed: validating: %s. status code: %f" % (urlObj.proxy, res.status_code))
        except Exception as e:
            speed = UNREACHABLE
            logging.debug("failed: validating: %s. (%s)" % (urlObj.proxy, str(e)))
        finally:
            if speed < UNREACHABLE:
                urlObj.speed = speed
            else:
                urlObj.speed += speed
            urlObjs_res.append(urlObj)
    return urlObjs_res

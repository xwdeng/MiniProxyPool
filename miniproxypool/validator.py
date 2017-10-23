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
# todo: using aiohttp
async def _get_respons_with_proxy_aiohttp(urlObj):
    cur_speed = 0
    try:
        async with aiohttp.ClientSession() as session: #todo: proxy could be https? #urlObj.proxy #proxy="http://" + urlObj.proxy,
            async with session.get(urlObj.url, headers = urlObj.headers, timeout = VALIDATOR_TIMEOUT) as response:
                randWait = random.uniform(0, 2)
                await asyncio.sleep(randWait)
                start = time.time()
                resp = await response.text()
                if response.status == 200:
                    cur_speed = time.time() - start
                    logging.debug("[%s] succeeded: validating: %s, speed: %f" % (multiprocessing.current_process().name, urlObj.proxy, cur_speed))
                else:
                    logging.debug("failed: validating: %s, STATUS_CODE: %d" % (urlObj.proxy, response.status))
                    cur_speed = UNREACHABLE

    except Exception as e:
        cur_speed = UNREACHABLE
        logging.debug("failed: validating: %s, (%s)" % (urlObj.proxy, str(e)))

    if cur_speed < UNREACHABLE:  # this 'weird' policy is used for clean the DB
        urlObj.speed = cur_speed
    else:
        urlObj.speed += cur_speed
    return urlObj

# todo: using aiohttp
def validate_proxy_list_aiohttp(urlObjs):
    loop = asyncio.get_event_loop()
    tasks = []
    for taskURL in urlObjs:
        tasks.append(asyncio.ensure_future(_get_respons_with_proxy_aiohttp(taskURL)))

    loop.run_until_complete(asyncio.wait(tasks))
    res = [];
    for t in tasks:
        res.append(t.result())
    return res

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

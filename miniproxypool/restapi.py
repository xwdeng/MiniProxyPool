#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
import re
import logging
import json
import miniproxypool.config

logger = logging.getLogger(__name__)
proxypool_inst = None


def proxy_entry_to_dict(proxy_entry):
    proxy_dict = {
        'ip': proxy_entry[0],
        'port': proxy_entry[1],
        'speed': proxy_entry[2]
    }
    return proxy_dict


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.search(miniproxypool.config.REST_API_PATH_GET_ALL_VALID, self.path) is not None:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            proxies_list = proxypool_inst.get_valid_proxies()
            proxies_dicts = []
            for proxy in proxies_list:
                proxies_dicts.append(proxy_entry_to_dict(proxy))
            self.wfile.write(json.dumps(proxies_dicts).encode('utf-8'))
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer:
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)

    def start(self):

        self.server_thread.daemon = True
        self.server_thread.start()

    def wait_for_thread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.wait_for_thread()


def start_rest_api_thread(proxypool):
    global proxypool_inst
    proxypool_inst = proxypool
    server = SimpleHttpServer(miniproxypool.config.REST_SRV_IP, miniproxypool.config.REST_SRV_PORT)
    logger.warning('Restful API Server running at [%s:%d] ...' % (miniproxypool.config.REST_SRV_IP, miniproxypool.config.REST_SRV_PORT))
    logging.warning("Restapi to get all valid proxies: GET http://%s:%d/api/v1/proxies" % ("localhost", miniproxypool.config.REST_SRV_PORT))

    server.start()
    server.wait_for_thread()
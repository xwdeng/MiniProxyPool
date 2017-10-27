#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.

from .sqlitedb import SqliteDB
import logging
import miniproxypool.config
import threading

class ProxyDB(SqliteDB):
    def __init__(self):
        super().__init__()
        self.table_name = 'proxy'

    def create_table_proxy(self):
        values = '''
                   ip varchar(20) NOT NULL,
                   port varchar(11) NOT NULL,
                   protocol varchar(10) NOT NULL DEFAULT http,
                   speed int(11) NOT NULL DEFAULT 0,
                   updated_time TimeStamp NOT NULL DEFAULT (datetime(\'now\',\'localtime\')),
                   created_time TimeStamp NOT NULL DEFAULT '0000-00-00 00:00:00',
                   PRIMARY KEY (ip,port)
               '''
        query = "CREATE TABLE IF NOT EXISTS %s(%s)" % (self.table_name, values)
        self.cursor.execute(query)
        query = '''
                   CREATE INDEX IF NOT EXISTS proxy_index on %s (protocol, speed, updated_time, created_time);
                   CREATE TRIGGER IF NOT EXISTS proxy_update_trig AFTER UPDATE OF speed ON %s
                       BEGIN
                         UPDATE %s SET updated_time=datetime(\'now\',\'localtime\') WHERE ip=NEW.ip AND port=NEW.port;
                       END;
                   CREATE TRIGGER IF NOT EXISTS proxy_insert_trig AFTER INSERT ON %s
                       BEGIN
                         UPDATE %s SET created_time=datetime(\'now\',\'localtime\') WHERE ip=NEW.ip and port=NEW.port;
                       END;
               '''%( self.table_name, self.table_name, self.table_name, self.table_name, self.table_name)
        self.cursor.executescript(query)


    # add one proxy entry in the table
    def add_new_proxy(self, ip, port, protocol, speed):
        args = [ {
                'data': {
                    'ip':ip,
                    'port':port,
                    'protocol': protocol,
                    'speed': speed
                        }
                } ]
        errs = self.insert(self.table_name, args)
        if errs[0] == 'success':
            logging.debug("new proxy added: %s:%s"%(ip, port))
            return True
        else:
            return False

    # get all proxies in the table
    # Note: This is a thread-safe method.
    def get_all_proxies(self):
        return self.select_threadsafe(self.table_name, {'field':['ip', 'port', 'speed'] , 'where':None, 'order': ['speed ASC'], 'limit':None})

    def get_valid_proxies(self):
        return self.select_threadsafe(self.table_name,
                                      {'field': ['ip', 'port', 'speed'], 'where': [('speed', '<=', miniproxypool.config.VALIDATOR_TIMEOUT), ('speed', '>=', 0)], 'order': ['speed ASC'], 'limit': None})

    def delete_invalided_proxies(self):
        return self.delete(self.table_name, {'where':[('speed', '>=', 500)]})

    def update_proxies(self, proxies):
        """
        :param proxies:
            example:
               [
                 {'ip': 123.123.123.123,
                  'port': 123,
                  'protocol': "http",
                  'speed': 1.2,
                  },
                  ...
               ]
        :return: 
        """
        args = []
        args.extend([ {'data': proxy, 'where':[('ip', '=', proxy['ip']),('port', '=', proxy['port'])]}  for proxy in proxies])
        errs = self.update(self.table_name, args)
        logging.debug("updated %d proxy entries." % (len(proxies)))
        return errs


    def update_proxy(self, ip, port, protocol, speed):
        #todo: change
        proxies = [{
            'ip': ip,
            'port': port,
            'protocol': protocol,
            'speed': speed
        }]
        self.update_proxies(proxies)


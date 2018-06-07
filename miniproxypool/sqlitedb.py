#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Auther: Xiaowei Deng
#
# This file is part of Mini Proxy Pool
#
# This program is free software and it is distributed under
# the terms of the MIT license. Please see LICENSE file for details.

# This module provide the basic interface for accessing SqliteDB
import sqlite3
import threading
import logging

logger = logging.getLogger(__name__)


class SqliteDB(object):
    def __init__(self):
        self.lock = threading.Lock() #right now, only SELECT action is designed for multi-threading.

    def init_dbconn(self, db_file):
        """
        create database and also make the connection
        :param db_file:
        :return:
        """
        self.db_file = db_file
        self._conn = sqlite3.connect(self.db_file, check_same_thread=False)

    def create_table(self, table_name):
        """
        please override this function.
        :param table_name:
        :return:
        """
        pass

    def free(self):
        self._conn.close()

    def select_threadsafe(self, table_name, conds):
        """
        SQL syntax: SELECT col1, col2, ... FROM table_name WHERE col1 > num1, ...

        :param table_name:
        :param conds: dictionary with all the needed parameter for SQL query.
            example:
            {
              'where' : [ ('col1', '>', 100), ('col2', '>', 200), ...],
              'order' : [ 'col1 ASC','col2 DESC' ...],
              'limit' : 20
             }
        :return:
        """
        try:
            self.lock.acquire()
            cursor = self._conn.cursor()
            vals = []
            query = "SELECT %s" % (','.join(conds['field']))
            query += " FROM %s" % table_name
            if conds['where']:
                query += ' WHERE ' + ' and '.join(['%s %s ?' % n[:2] for n in conds['where']])
                vals.extend([n[-1] for n in conds['where']])
            if conds['order']:
                query += ' ORDER BY ' + ','.join(conds['order'])
            if conds['limit']:
                query += ' LIMIT ?'
                vals.append(conds['limit'])

            data = cursor.execute(query, vals).fetchall()
        except Exception as e:
            data = []
        finally:
            cursor.close()
            self.lock.release()

        return data

    def insert(self, table_name, args):
        """
        Insert multi rows into DB.

        SQL syntax: INSERT INTO table_name (col1,col2,...) VALUES(val1, val2,..)

        :param table_name:
        :param datas:
        example:
            [
              {
                    'data': {'col1':val1, 'col2':val2, ...}
              },
              ...
            ]
        :return:
        """
        try:
            self.lock.acquire()
            cursor = self._conn.cursor()
            result = []
            for arg in args:
                data = arg['data']
                cols = ','.join([k for k in data])
                qmarks = ','.join(['?' for l in data])
                vals = tuple([data[k] for k in data])
                query = "INSERT INTO %s" % table_name
                query += " (%s) VALUES(%s)"% (cols, qmarks)
                try:
                    cursor.execute(query, vals)
                    result.append('success')
                except Exception as execute_e:
                    result.append(execute_e)
                    # if 'UNIQUE constraint' in e.args[0]:
                    #    err = "%s:%s already in DB" % (arg['ip'], arg['port'])
            self._conn.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            self.lock.release()
            return result

    def update(self, table_name, args):
        """
        :param table_name:
        :param args:
            [
                {
                     'data': {'col1':val1, 'col2':val2, ...},
                    'where': [ ('col1', '>', 100), ('col2', '<', 200), ...],
                },
                ...
            ]
        :return:
        """
        try:
            self.lock.acquire()
            cursor = self._conn.cursor()
            result = []
            for arg in args:
                vals = []
                data = arg['data']
                updates = ','.join(['%s=?' % k for k in data])
                vals.extend([data[k] for k in data])
                conds = ' and '.join([ "%s %s ?" % (k[0], k[1]) for k in arg['where']])
                vals.extend(["%s"%k[2] for k in arg['where']])
                query = "UPDATE %s" % table_name
                query += " SET %s WHERE %s" % (updates, conds)
                try:
                    cursor.execute(query, vals)
                    result.append('success')
                except Exception as e:
                    result.append(e)
            self._conn.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            self.lock.release()
            return result

    def delete(self, table_name, cond_where):
        """

        :param table_name:
        :param cond_where: dictionary with all the needed parameter for SQL query.
            example:
            {
              'where' : [ ('col1', '>', 100), ('col2', '>', 200), ...],
             }
        :return:
        """
        try:
            self.lock.acquire()
            cursor = self._conn.cursor()
            vals = []
            query = 'DELETE FROM %s' % table_name
            if cond_where['where']:
                query += ' WHERE ' + ' and '.join(['%s %s ?' % n[:2] for n in cond_where['where']])
                vals.extend([n[-1] for n in cond_where['where']])

            result = cursor.execute(query, vals).fetchall()
            self._conn.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            self.lock.release()
            return result

    def executesql(self, query):
        try:
            self.lock.acquire()
            cursor = self._conn.cursor()
            result = cursor.execute(query)
            self._conn.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            self.lock.release()
            return result

    def executescript(self, query):
        try:
            self.lock.acquire()
            cursor = self._conn.cursor()
            result = cursor.executescript(query)
            self._conn.commit()
        except Exception as e:
            raise e
        finally:
            cursor.close()
            self.lock.release()
            return result

    def disconnect(self):
        self._conn.close()

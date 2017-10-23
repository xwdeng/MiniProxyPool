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
class SqliteDB(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.queries = {
            #'SELECT': 'SELECT %s FROM %s',
            #'INSERT': 'INSERT INTO %s (%s) VALUES(%s)',
            #'UPDATE': 'UPDATE %s SET %s WHERE %s',
            #'DELETE': 'DELETE FROM %s where %s',
            'DELETE_ALL': 'DELETE FROM %s',
            'CREATE_TABLE': 'CREATE TABLE IF NOT EXISTS %s(%s)',
        }

    def init_dbconn(self, db_file):
        self.db = sqlite3.connect(db_file, check_same_thread=False)
        self.db_file = db_file
        self.cursor = self.db.cursor()

    def create_table(self, table_name):
        pass

    def free(self):
        self.cursor.close()

    def select_threadsafe(self, table_name, args):
        """
        SQL syntax: SELECT col1, col2, ... FROM table_name WHERE col1 > num1, ...

        :param table_name:
        :param args:
        :return:
        """
        vals = []
        query = "SELECT %s" % (','.join(args['field']))
        query += " FROM %s" % table_name
        if args['where']:
            query += ' WHERE ' + ' and '.join(['%s %s ?' % n[:2] for n in args['where']])
            vals.extend([n[-1] for n in args['where']])
        if args['order']:
            query += ' ORDER BY ' + ','.join(args['order'])
        if args['limit']:
            query += ' LIMIT ?'
            vals.append(args['limit'])

        self.lock.acquire()
        try:
            data = self.cursor.execute(query, vals).fetchall()
        finally:
            self.lock.release()
            return data


    def insert(self, table_name, args):
        """
        SQL syntax: INSERT INTO table_name (col1,col2,...) VALUES(val1, val2,..)

        :param table_name:
        :param args:
        :return:
        """
        result = []
        for arg in args:
            cols = ','.join([k for k in arg])
            values = ','.join(['?' for l in arg])
            vals = tuple([arg[k] for k in arg])
            query = "INSERT INTO %s" % table_name
            query += " (%s) VALUES(%s)"% (cols, values)
            try:
                self.cursor.execute(query, vals)
                result.append('success')
            except Exception as e:
                #if 'UNIQUE constraint' in e.args[0]:
                #    err = "%s:%s already in DB" % (arg['ip'], arg['port'])
                result.append(e)
        self.db.commit()
        return result

    def update(self, table_name, args):
        """
        SQL syntax: UPDATE table_name SET col1 = val1, ... WHERE conds

        :param table_name:
        :param args:
        :return:
        """
        result = []
        for arg in args:
            updates = ','.join(['%s=?' % k for k in arg])
            conds = ' and '.join(['%s=?' % k for k in arg if k == 'ip' or k == 'port'])
            vals = [arg[k] for k in arg]
            subs = [arg[k] for k in arg if k == 'ip' or k == 'port']
            query = "UPDATE %s" % table_name
            query += " SET %s WHERE %s" % (updates, conds)
            try:
                self.cursor.execute(query, vals + subs)
                result.append('success')
            except Exception as e:
                result.append(e)
        self.db.commit()
        return result

    def delete(self, table_name, condition):
        vals = []
        query = 'DELETE FROM %s' % table_name
        if condition['where']:
            query += ' WHERE ' + ' and '.join(['%s %s ?' % n[:2] for n in condition['where']])
            vals.extend([n[-1] for n in condition['where']])

        result = self.cursor.execute(query, vals).fetchall()
        self.db.commit()
        return result

    def executesql(self, query):
        result = self.cursor.execute(query).fetchall()
        self.db.commit()
        return result

    def _cursor_executes_qmark_threadsafe(self, query_qmark, vals):
        self.lock.acquire()
        try:
            result = self.cursor.execute(query_qmark, vals).fetchall()
        finally:
            self.lock.release()
            return result

    def disconnect(self):
        self.db.close()

import unittest

from miniproxypool import proxydb
from multiprocessing.pool import ThreadPool
import time
import random
import os


class TestProxyDB(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self._proxies = None

    def _load_data(self):
        if self._proxies is not None:
            return

        self._proxies = []
        port = 10
        for i in range(1, 1000):
            ip = "192.168.120.1"
            port += 1
            protocol = "http"
            speed = random.random()
            self._proxies.append((ip, port, protocol, speed))

    def setUp(self):
        self._load_data()
        self._proxydb = proxydb.ProxyDB()
        self._proxydb.init_dbconn("_test.db")
        self._proxydb.create_table_proxy()

    def tearDown(self):
        self._proxydb.free()
        os.remove("_test.db")

    def test_db_basic(self):
        """
        test basic read and write
        """
        ip = "192.168.120.1"
        port = '1010'
        protocol = "http"
        speed = 1.0
        self._proxydb.add_new_proxy(ip, port, protocol, speed)
        proxies_list = self._proxydb.get_all_proxies()
        self.assertEqual(len(proxies_list), 1)
        self.assertEqual(proxies_list[0][0], ip)
        self.assertEqual(proxies_list[0][1], port)
        self.assertEqual(proxies_list[0][2], speed)

    def _add_one_proxy(self, proxy_entry):
        """
        helper function to write a single proxy_entry
        """
        random_time = random.random() / 100.0
        time.sleep(random_time)
        self._proxydb.add_new_proxy(proxy_entry[0], proxy_entry[1], proxy_entry[2], proxy_entry[3])

    def test_multi_thread_db_write(self):
        """
        test multi-thread write

        todo: add multi-read here
        """
        _thread_pool = ThreadPool(15)
        _thread_pool1 = ThreadPool(5)
        r = _thread_pool.map_async(self._add_one_proxy, self._proxies)
        r.wait()


if __name__ == '__main__':
    unittest.main()

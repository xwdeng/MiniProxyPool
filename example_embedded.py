import miniproxypool
import logging
import sys
import time
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)10s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)

if __name__ == '__main__':
    miniproxypool.config.VALIDATOR_URL = "http://www.google.ca"
    miniproxypool.run_as_daemon()

    while(True):
        time.sleep(60*30)
        logging.info("There are %d valid proxies in the pool."%len(miniproxypool.get_all_proxies()))
    #print(miniproxypool.get_all_proxies())


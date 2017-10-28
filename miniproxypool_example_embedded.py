import miniproxypool
import logging
import sys
import time
import requests
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(name)20.20s] [%(asctime)s] [%(levelname)7.7s] [%(threadName)10s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)
logging.getLogger('requests').setLevel(logging.WARNING) # suppress the logger from requests

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    miniproxypool.config.VALIDATOR_URL = "http://www.google.ca"
    miniproxypool.config.VALIDATOR_TIMEOUT = 0.5  # seconds
    miniproxypool.config.VALIDATOR_THREAD_POOL_SIZE = 20
    miniproxypool.config.VALIDATOR_CONNECTIONS_PER_THREAD = 20
    miniproxypool.config.VALIDATE_THREAD_RUN_PERIOD = 5 * 60  # seconds wait after each validation
    miniproxypool.config.LOAD_FROM_SITES_THREAD_RUN_PERIOD = 10 * 60  # seconds wait after each loading from sites
    miniproxypool.run_as_daemon()

    while(True):
        print("There are %d valid proxies in the pool."%len(miniproxypool.get_all_proxies()))
        time.sleep(60 * 10)
    #print(miniproxypool.get_all_proxies())


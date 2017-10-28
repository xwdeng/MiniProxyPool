import miniproxypool
import logging
import sys
import time
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(name)20.20s] [%(asctime)s] [%(levelname)7.7s] [%(threadName)10s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)
import requests

if __name__ == '__main__':
    miniproxypool.config.REST_SRV_IP = "0.0.0.0"
    miniproxypool.config.REST_SRV_PORT = 9876
    miniproxypool.config.VALIDATOR_URL = "http://www.google.ca"
    miniproxypool.run_as_daemon()
    miniproxypool.run_rest_api_serv()

    while(True):
        time.sleep(5)
        # test and print the valid proxies from restapi
        r = requests.get(miniproxypool.rest_api_url_get_all_valid_proxiex())
        print(r.text)


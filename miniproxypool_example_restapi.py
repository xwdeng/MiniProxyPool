import miniproxypool
import logging
import sys
import time
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)10s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)

if __name__ == '__main__':
    miniproxypool.config.REST_SRV_IP = "0.0.0.0"
    miniproxypool.config.REST_SRV_PORT = 9876
    miniproxypool.config.VALIDATOR_URL = "http://www.google.ca"
    miniproxypool.run_as_daemon()
    miniproxypool.run_rest_api_serv()

    logging.info("Proxy pool is running and can be fetched at:http://%s:%d/api/v1/proxies" % (miniproxypool.config.REST_SRV_IP, miniproxypool.config.REST_SRV_PORT))

    while(True):
        # Because all the services is running as daemon threads, main threads should always be running...
        time.sleep(60*30)

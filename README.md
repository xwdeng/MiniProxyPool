# Mini Proxy Pool
The Mini Proxy Pool is a package to help provide valid proxy server resources.

# Main Feature
Here are just a few of the things that Mini Proxy Pool does well:

- Light-weighted
  The main purpose of this project is to provide a simple way to maintain an active proxy pool with high quality proxy server resources. Proxies sources can be from both websites or files.

- Easy embedded in your own project  
  All the services in this package are running as daemon services. It is easy to setup the proxy into other projects.

- Restful service  
  The Mini Proxy Pool service could also run as a dedicated server to provide restful service.


# Quick Start
## Using Mini Proxy Pool as part of your own project
```python
import miniproxypool
import logging
import sys
import time
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)10s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)

if __name__ == '__main__':
    miniproxypool.config.VALIDATOR_URL = "http://www.google.ca"
    miniproxypool.run_as_daemon()

    # your own code here:
    while(True):
        time.sleep(60*30)
        logging.info("There are %d valid proxies in the pool."%len(miniproxypool.get_all_proxies()))

```

## Using Mini Proxy Pool as a dedicated proxy pool server
```python
import miniproxypool
import logging
import sys
import time
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(threadName)10s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)

if __name__ == '__main__':
    miniproxypool.config.VALIDATOR_URL = "http://www.google.ca"
    miniproxypool.run_as_daemon()
    miniproxypool.run_rest_api_serv()
    
    # your own code here:
    while(True):
        time.sleep(60*30)
        logging.info("There are %d valid proxies in the pool."%len(miniproxypool.get_all_proxies()))

    
```

# How to use
## Import the miniproxypool package
```python
import miniproxypool
```
## Config the important parameters

### Threads running policy
```python
miniproxypool.config.VALIDATE_THREAD_RUN_PERIOD = 5 # seconds wait after each validation
miniproxypool.config.LOAD_FROM_SITES_THREAD_RUN_PERIOD = 3 # seconds wait after each loading from sites
miniproxypool.config.VALIDATOR_THREAD_POOL_SIZE = 20 # thread pool size for validation task
miniproxypool.config.VALIDATOR_CONNECTIONS_PER_THREAD = 20 # number of proxies that each thread should deal with

```

### Validator Policy  
```python
miniproxypool.config.VALIDATOR_TIMEOUT = 1 # timeout for each proxy testing
miniproxypool.config.VALIDATOR_URL = "http://www.google.ca" # url used for each proxy testing
```

### Invalid Proxy Policy
```python
miniproxypool.config.INVALID_PROXY_TIMES = 5 # if a proxy cannot be connected for VALIDATOR_DEFINE_INVALID_TIMES time, it is defined as invalid
miniproxypool.config.INVALID_PROXY_IF_DELETE = True # at the end each validation cycle, whether to delete invalid proxy in DB
```

### Restful Service  
```python
miniproxypool.config.REST_SRV_IP = "0.0.0.0"
miniproxypool.config.REST_SRV_PORT = 9876
```

### Proxy Sources

- From websites  
*note:* the following code fragment is used in the package to extract proxies in the website:

```python
url_base = site['url_base']
pattern = re.compile(site['pattern'])
ip_ind = site['ip_ind']
port_ind = site['port_ind']
for match in pattern.findall(r.text):
    ip = match[ip_ind]
    port = match[port_ind]
    ...
    ...


```
 
```python
miniproxypool.config.PROXY_SOURCE_SITES = [
        {
            'url_base': "https://free-proxy-list.net",
            'pattern': "((?:\d{1,3}\.){1,3}\d{1,3})<\/td><td>(\d{1,6})(.{1,200})<td class='hx'>(.{2,3})",
            'ip_ind': 0,
            'port_ind': 1
        },
        {
             'url_base': 'https://www.us-proxy.org',
             'pattern': "((?:\d{1,3}\.){1,3}\d{1,3})<\/td><td>(\d{1,6})(.{1,200})<td class='hx'>(.{2,3})",
             'ip_ind': 0,
             'port_ind': 1
        },
        {
            'url_base': "http://spys.me/proxy.txt",
            'pattern': '((?:\d{1,3}\.){1,3}\d{1,3}):(\d{1,6})',
            'ip_ind': 0,
            'port_ind': 1
        }
]
```

- From local files  
```python
miniproxypool.config.PROXY_SOURCE_FILES = [
    'custom_proxies_list.txt'
]
```
example of proxy file:  
```python
# Add proxy list here
# e.g.
# 110.110.110.110:1234
1.2.3.4:123
5.6.7.8:567
```

## Get all valid proxies
### Embedded API
```python
miniproxypool.get_all_proxies()
```
### Rest API
Rest api address: `miniproxypool.rest_api_url_get_all_proxies()`

# Todo List
- Add documentations for the source codes
- Add http/https protocol mark when loading proxy from sites
- Add more options in restful api
- Add aiohttp support for faster validation
- Add test scripts

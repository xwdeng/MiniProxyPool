import miniproxypool
import logging
import sys
import time
from time import gmtime, strftime

import requests
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='[%(name)20.20s] [%(asctime)s] [%(levelname)7.7s] [%(threadName)10s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S',)
logging.getLogger('requests').setLevel(logging.WARNING) # suppress the logger from requests

logger = logging.getLogger(__name__)

def create_index_html(proxies_list):
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Proxy List</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</head>
<body>

<div class="container">
  <h2>Proxy List</h2>
    """
    html += "<h5>[Last time updated: %s (GMT)]</h5>" % strftime("%Y-%m-%d %H:%M:%S", gmtime())
    html += """
  <table class="table table-striped">
  <thead>
    <tr>
      <th>#</th>
      <th>IP</th>
      <th>PORT</th>
      <th>SPEED</th>
    </tr>
  </thead>
  <tbody>
    """
    cnt = 1;
    for proxy in proxies_list:
        html += "<tr>\n";
        html +="<th scope=\"row\">%d</th>\n"%cnt
        html +="<td>%s</td>\n"%proxy[0]
        html +="<td>%s</td>\n"%proxy[1]
        html +="<td>%.3f</td>\n"%proxy[2]
        html +="</tr>\n"
        cnt += 1;

    html += """
    </tbody>
</table>
</div>

</body>
</html>
    """
    return html



if __name__ == '__main__':
    miniproxypool.config.VALIDATOR_URL = "http://www.google.ca"
    miniproxypool.config.VALIDATOR_TIMEOUT = 0.5  # seconds
    miniproxypool.config.VALIDATOR_THREAD_POOL_SIZE = 20
    miniproxypool.config.VALIDATOR_CONNECTIONS_PER_THREAD = 20
    miniproxypool.config.VALIDATE_THREAD_RUN_PERIOD = 5 * 60  # seconds wait after each validation
    miniproxypool.config.LOAD_PORXIES_FROM_SOURCES_THREAD_RUN_PERIOD = 10 * 60  # seconds wait after each loading from sites
    miniproxypool.run_as_daemon()

    while(True):
        filepath = "index.html"
        file = open(filepath, "w")
        file.write(create_index_html(miniproxypool.get_all_proxies()))
        file.close()
        print("File '%s' updated." % filepath)
        time.sleep(60 * 10)
    #print(miniproxypool.get_all_proxies())


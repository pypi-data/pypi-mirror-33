################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

from __future__ import print_function

import plac
import base64
import json
import time
import requests
from pp.client.python.logger import getLogger

@plac.annotations(
    server_url=('URL of Produce & Publish API)', 'option', 's')
)
def version(server_url='http://localhost:6543'):
    if server_url.endswith('/'):
        server_url = server_url[:-1]
    return requests.get(server_url + '/api/version')

def main():
    print(plac.call(version))

if __name__ == '__main__':
    main()

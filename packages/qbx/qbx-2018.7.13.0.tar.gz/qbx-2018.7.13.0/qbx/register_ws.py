import json
import socket

import requests
from docopt import docopt as docoptinit

register_kong_doc = """
Usage:
    register_ws [options]
    
Options:
    --ot             1Token Endpoint (it will only register into  config:v1ws also)
    --v2             Register to v2
    --name=<name>
    --uri=<uri>
    --ip=<ip>
    --port=<port>
"""


def register_ws(argv):
    docopt = docoptinit(register_kong_doc, argv)
    print(docopt)
    dst_list = []
    if docopt['--v2']:
        dst_list.append('wsv2')
    if docopt['--ot']:
        dst_list.append('v1ws')
    for dst in dst_list:
        print('check', dst)
        r = requests.get(f'http://api.qbtrade.org/redis/get?key=config:{dst}&raw=1')
        if r.status_code != 200:
            import logging
            logging.warning('status 200 fail')
            return
        r = r.json()
        print('get', r)
        port = docopt['--port']
        if not docopt['--ip']:
            ip = socket.gethostbyname(socket.gethostname())
        else:
            ip = docopt['--ip']
        uri = docopt['--uri']
        r[docopt['--name']] = f'ws://{ip}:{port}/{uri}'
        print('new record', r)

        data = {'key': f'config:{dst}', 'value': json.dumps(r)}
        print('going to set', data)
        r = requests.post('http://api.qbtrade.org/redis/set', data)
        print(r.json())


if __name__ == '__main__':
    # register_kong(['--name', 'pytest', '--ip', '1.2.3.4', '--uris', '/pytest', '--port', '8080'])
    register_ws(['--name', '/pytest', '--uri', '/ws', '--port', '3000'])

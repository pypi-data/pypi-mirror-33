import requests
from docopt import docopt as docoptinit

options = """
Usage:
    register_kong [options]
    
Options:
    --file=<file>
    --target=<target>
"""


def upload(argv):
    docopt = docoptinit(options, argv)
    file = docopt['--file']
    target = docopt['--target']
    if not target:
        index = file.rfind('/')
        if index > 0:
            target = file[index + 1:]
        else:
            target = file
    url = f'http://api.qbtrade.org/oss/public/{target}'

    requests.post(url, files={
         "file": open(file, 'rb')
    })

import asyncio
import sys

import jwt
from aiohttp import web, ClientSession
from docopt import docopt as docoptinit

bad_headers = ()

auth_jwt_doc = """
Usage:
    auth_wrapper [options]
    
Options:
    --port=<port>               listen port
    --dest=<dest>               upstream as form as {host}:{port}
    --debug                     using debug pub and private
    --name=<name>               server symbol
    --noauth                    Ignore jwt auth, for debug purpose
"""

debug_pub = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDvWEO0amFTUXJdF6TsevXNfxEg
is9YfaRzAVef9Dm3CeJKdXqS/KCP1/8iw2tcRWGEY1MiCwp3cegwujWnDr869cCh
FccrhRcWEVwCPEioosvMTajJSgn0nGGZf6HC/qDMT1ESiD0VlWa1miF457mXXbS0
/jKAYJBiCAKU8g+OZQIDAQAB
-----END PUBLIC KEY-----
"""

debug_pri = """
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQDvWEO0amFTUXJdF6TsevXNfxEgis9YfaRzAVef9Dm3CeJKdXqS
/KCP1/8iw2tcRWGEY1MiCwp3cegwujWnDr869cChFccrhRcWEVwCPEioosvMTajJ
Sgn0nGGZf6HC/qDMT1ESiD0VlWa1miF457mXXbS0/jKAYJBiCAKU8g+OZQIDAQAB
AoGAdAS9DP9kHhck8Ks9bsRL0kj97GBdEfAVfwnvh8HDGE7aOm2n9QgwbImvSxKf
QCMBmkLrUV04vZ2hh707tLcZSnM/ulOkLGsytPruM5h9cnV3lhsNLt4jtuSlDvVz
j9Z4mxXOVidjNq41Pg4qKDQS8q/vB+x7DtEn/4zvBotr1QECQQD8aswh5yn9RDao
rMiNmHmh2ldSarbJcZFzsQoX9CK3el+oo7XRguBglwRFHDBNIAh92fUiX4KATZRF
QrIzQnhJAkEA8r33Wd/gZj5GH+AJ/K9zYU4yXYdbMdwaHU/D/XrpfxqtxqQ9h6e4
pNLyOStEnwXPD4voL92aLOwW5Dg34xO9PQJBAKphOEsGK0yeV7rBblpNeoSqydiC
2cDd3M1XyjVjAHAStTEy2A6EpgnsxeAUZ/IXVkQE9Ddwerk6JIQfwgNhsakCQAT5
bZsy4kdWGVvH3IyID+Y7kv6lqnHAH+zf2JVWMni/VDZQ4U3pWvhNtlcDkvlrRg38
gPqSIPmwsNtmZ4bIvcUCQQDRybMD4BRDiZm8JG/gKwHwolUUCKtxjljwUiAq6J+A
t/7kQ94wZnOQDADVbcHs9vU/YRvBHUxF9Uky/Gs+Uzm9
-----END RSA PRIVATE KEY-----
"""

prod_pub = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAptDAATPBIAhmbuU5uJiH
Q/h3alX55fMHPynmxdXgvrPIg5Xv5VXuJBBCR99Tol5Wd/oiln0t+2Z167zy06GA
82Nb4Q/WggWOZGdp5asSihJnbN9eDWqo2J4ppyh9DBXgVB5OS1aaosbCIj0vnY8z
CVlFcr854ohllv7HYK1tTQadhnax02WvJJYPRyzITTHVtO99abpoMKj8GlpcZJ8d
Oe9Iy5h+i1wUCSulg/e4id9P0XBSN5iy1LcwL6BEj72qTA+egah0LrDpzHUnIMo3
+pniYhsJIlD8iSzICi5T2ca155zMsPv0KtuRii4TT21I3V9qY+G6Qwbe2BjZO3N0
JQIDAQAB
-----END PUBLIC KEY-----
"""


def start_proxy(port, dest, pub, name, noauth=False):
    def remove_bad_headers(headers):
        h = {}
        for key, value in headers.items():
            if key.lower() not in bad_headers:
                h[key] = value
        # h['Connection'] = "close"
        return h

    async def jwt_check(token):
        if noauth:
            return True
        print('check', token)
        if token is not None:
            payload = jwt.decode(token, key=pub, algorithms='RS256')
            print(f'name: {name}, path: {payload["permissions"]}')
            if name in payload['permissions']:
                return True
        return False

    async def auth_jwt(app, handler):
        async def do_it(request):
            print("==> %s" % dest)
            method = request.method
            path_qs = request.path_qs
            headers = remove_bad_headers(request.headers)
            cookies_str = headers.get('Cookie', '')
            data = await request.read()
            params = dict(request.query)
            cookies = {}
            for item in cookies_str.split(';'):
                sp = item.split('=')
                if len(sp) == 2:
                    cookies[sp[0].strip()] = sp[1].strip()
            print(cookies)
            auth = await jwt_check(cookies.get('jwt'))

            if not auth:
                r = {'code': 'auth-failed'}
                import json
                return web.Response(text=json.dumps(r), status=403)
            url = dest + path_qs
            if not url.startswith('http'):
                url = 'http://' + url

            print(app.loop, method, url, headers, data, params)
            return await get_resp(app.loop, method, url=url, headers=headers, data=data, params=params)

        return do_it

    async def get_resp(loop, method, url, headers=None, data=None, params=None):
        async with ClientSession(loop=loop) as session:
            async with session.request(method, url, headers=headers, data=data, params=params) as resp:
                body = await resp.read()
                headers = remove_bad_headers(resp.headers)
                # print(f"<== {method} {url} {dest} {resp.status} {body}")
                response = web.Response(body=body, status=resp.status, reason=resp.reason, headers=headers)
        return response

    async def init(loop, port):
        app = web.Application(loop=loop, middlewares=[auth_jwt])
        return await loop.create_server(app.make_handler(), "", port)

    def start():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(init(loop, port))
        loop.run_forever()

    start()


def auth_wrapper(argv):
    docopt = docoptinit(auth_jwt_doc, argv)
    print(docopt)
    port = int(docopt['--port'])
    dest = docopt['--dest']
    name = docopt['--name']
    if not dest.startswith('http'):
        raise Exception('--dest should starts with http;')
    if not name:
        raise Exception('--name must have')

    if docopt['--debug']:
        pub = debug_pub
    else:
        pub = prod_pub
    start_proxy(port, dest, pub, name, docopt['--noauth'])


if __name__ == "__main__":
    auth_wrapper(['--port', '3000', '--dest', 'http://konga.qbtrade.org', '--name', 'konga', '--noauth'])
    # auth_wrapper(['--port', '3000', '--dest', 'http://konga.qbtrade.org', '--name', 'konga', '--debug'])
    # auth_wrapper(sys.argv[1:])

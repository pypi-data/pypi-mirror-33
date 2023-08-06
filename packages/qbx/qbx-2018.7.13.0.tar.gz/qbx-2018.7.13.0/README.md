# upload to pypi
写好setup.py文件后，执行<center>`python setup.py sdist bdist_wheel upload`</center >
就可以上传到pypi服务器，执行命令后要求输入username和password。
有时候会出现bug，password验证不通过就需要配置~/.pypirc文件，格式如下  
```
[distutils]
index-servers =
    pypi
	
[pypi]
repository: https://pypi.python.org/pypi
username = <username>
password = <password>
```
配置完执行命令就会自动验证。


# upload

配置完成之后 使用 inv upload 来上传(需要pip install pyinvoke)

# Register Websocket

qbx register_ws --name /$endpoint --uri $uri --port $port

client will connect to api.qbtrade.org/wsv2/$endpoint

the proxy will to connect to $container:${port}/${uri}


## Example

qbx register_ws --name /candle --uri ws --port 3000

### Python Server Pesudo Code
server.listen('/ws', port=3000)

### Python Client Pesudo Code
ws_connect('ws://api.qbtrade.org/wsv2/candle')

# Baidu aip python sdk
# 安装
```
    Dev: pip install git+ssh://icode.baidu.com:8235/baidu/aip/api-python-sdk@master
    Release: pip install aip
```

# 使用
```
    aipOcr = AipOcr('你的 AppId', '你的 API Key', '你的 Secret Key')
    aipOcr.idcard(open('idcard.jpg', 'rb').read())
```
# Linux环境下提供aip_client
```
    aip_client
```
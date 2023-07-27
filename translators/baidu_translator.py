# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests
import random
import json
from hashlib import md5
from time import sleep

def create_client():
    print('百度翻译为您服务')
    with open('translator_keys/baidu_keys.json') as f:
        # Set your own appid/appkey.
        keys=json.load(f)
        appid = keys['id']
        appkey = keys['key']

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # payload = {'appid': appid, 'from': from_lang, 'to': to_lang, 'q': query, 'salt': salt, 'sign': sign}
    paras= {'action':'1','appid': appid, 'appkey':appkey,'from': 'en', 'to': 'zh', 'q': [], 'salt': [], 'sign': []} # action=1：使用自定义术语库

    class baidu_client(object):
        def __init__(self,h,p):
            self.headers=h
            self.p=p
        
        def doit(self,text):
            self.__query=text

            # Generate salt and sign
            def make_md5(s, encoding='utf-8'):
                return md5(s.encode(encoding)).hexdigest()

            self.__salt = random.randint(32768, 65536)
            self.__sign = make_md5(self.p['appid'] + self.__query + str(self.__salt) + self.p['appkey'] )

            self.p['q']=self.__query
            self.p['salt']=self.__salt
            self.p['sign']=self.__sign

            # Send request
            r = requests.post(url, params=self.p, headers=self.headers)
            result = r.json()
            return result['trans_result'][0]['dst']
        
    client=baidu_client(headers,paras)

    return client

def translator(client, text):
    sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
    return client.doit(text)


if __name__=="__main__": # 测试用
    c=create_client()
    t_en="THE ELECTRON KINETIC EQUATION".lower()

    t_zh=translator(c,t_en)
    print(t_en,'\n',t_zh)

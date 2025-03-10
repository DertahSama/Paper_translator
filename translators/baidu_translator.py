# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests,yaml,os,datetime,logging
import random
import json
from hashlib import md5
from time import sleep

def create_client():
    print('百度翻译为您服务')
    class baidu_client(object):
        def __init__(self):
            self.translator_name="baidu"
            logging.basicConfig(filename=f"log{datetime.datetime.now().strftime("%y%m")}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
            logging.warning("翻译器："+self.translator_name)
            
            with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)
            for apidir in config["翻译设置"]["翻译APIkeys文件夹"]:
                if os.path.exists(apidir):
                    print("[**] 读取API："+apidir+'/baidu_keys.yaml')
                    break
            with open(apidir+'/baidu_keys.yaml') as f:
                # Set your own appid/appkey.
                keys=yaml.load(f,Loader=yaml.Loader)
                appid = keys['id']
                appkey = keys['key']

            endpoint = 'http://api.fanyi.baidu.com'
            path = '/api/trans/vip/translate'
            self.url = endpoint + path

            # Build request
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            # payload = {'appid': appid, 'from': from_lang, 'to': to_lang, 'q': query, 'salt': salt, 'sign': sign}
            paras= {'action':'1','appid': appid, 'appkey':appkey,'from': 'en', 'to': 'zh', 'q': [], 'salt': [], 'sign': []} # action=1：使用自定义术语库
            self.headers=headers
            self.p=paras
        
        def trans_text(self,text):
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
            r = requests.post(self.url, params=self.p, headers=self.headers)
            result = r.json()
            return result['trans_result'][0]['dst']
        
    client=baidu_client()

    return client

def translator(client, text):
    sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
    return client, client.doit(text)


if __name__=="__main__": # 测试用
    c=create_client()
    t_en="THE ELECTRON KINETIC EQUATION".lower()

    t_zh=c.trans_text(t_en)
    print(t_en,'\n',t_zh)

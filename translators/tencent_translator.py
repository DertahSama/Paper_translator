from tencentcloud.common import credential
from tencentcloud.tmt.v20180321 import tmt_client, models
from time import sleep

import json,os,yaml,logging,datetime

# =========== 腾讯翻译API==========
#  安装： pip3.11 install --upgrade tencentcloud-sdk-python

def create_client():
    print('[**] 腾讯翻译为您服务')
    # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
    # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
    # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
    
    class TencentClient(tmt_client.TmtClient):
        def __init__(self):
            self.translator_name="tencent"
            logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
            logging.warning("翻译器："+self.translator_name)
            
            with open('设置.yaml', 'r',encoding="utf8") as file: self.config=yaml.load(file,Loader=yaml.Loader)
            for apidir in self.config["翻译设置"]["翻译APIkeys文件夹"]:
                if os.path.exists(apidir):
                    print("[**] 读取API："+apidir+'/tencent_keys.yaml')
                    break
            print("[**] 术语表id："+str(self.config["翻译设置"]["tencent-要用的术语表id"]))
            
            with open( apidir+'/tencent_keys.yaml', 'r',encoding="utf8") as file:
                self.keys=yaml.load(file,Loader=yaml.Loader)
            
            cred = credential.Credential(self.keys['id'], self.keys['key'])
            
            super().__init__(cred, "ap-beijing")
        
        def trans_text(self,en):
            req = models.TextTranslateRequest()
            params = {
                "Source": "en",
                "Target": "zh",
                "ProjectId": 0,
                "SourceText": en,
                "TermRepoIDList":self.config["翻译设置"]["tencent-要用的术语表id"],
            }
            req.from_json_string(json.dumps(params))

            # 返回的resp是一个TextTranslateBatchResponse的实例，与请求对象对应
            resp = self.TextTranslate(req)

            # 输出
            text_zh=resp.TargetText
            return text_zh
            


    return TencentClient()

# def translator(client,text):
#     # 实例化一个请求对象,每个接口都会对应一个request对象
#     req = models.TextTranslateRequest()
#     params = {
#         "Source": "en",
#         "Target": "zh",
#         "ProjectId": 0,
#         "SourceText": text
#     }
#     req.from_json_string(json.dumps(params))

#     # 返回的resp是一个TextTranslateBatchResponse的实例，与请求对象对应
#     resp = client.TextTranslate(req)

#     # 输出
#     text_zh=resp.TargetText
#     sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
#     return client, text_zh

if __name__=="__main__": # 测试用
    c=create_client()
    t_en="THE ELECTRON KINETIC EQUATION"

    t_zh=c.trans_text(t_en)
    print(t_en,'\n',t_zh)
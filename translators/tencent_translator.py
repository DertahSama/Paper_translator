from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
from time import sleep

import json

# =========== 腾讯翻译API==========
#  安装： pip3.11 install --upgrade tencentcloud-sdk-python

def create_client():
    print('腾讯翻译为您服务')
    # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
    # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
    # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
    with open("translator_keys/tencent_keys.json") as f:
        keys=json.load(f)

    cred = credential.Credential(keys['id'], keys['key'])
    # 实例化一个http选项，可选的，没有特殊需求可以跳过
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tmt.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # 实例化要请求产品的client对象,clientProfile是可选的
    client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

    return client

def translator(client,text):
    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = models.TextTranslateRequest()
    params = {
        "Source": "en",
        "Target": "zh",
        "ProjectId": 0,
        "SourceText": text
    }
    req.from_json_string(json.dumps(params))

    # 返回的resp是一个TextTranslateBatchResponse的实例，与请求对象对应
    resp = client.TextTranslate(req)

    # 输出
    text_zh=resp.TargetText
    sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
    return text_zh

if __name__=="__main__": # 测试用
    c=create_client()
    t_en="THE ELECTRON KINETIC EQUATION"

    t_zh=translator(c,t_en)
    print(t_en,'\n',t_zh)
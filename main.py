from PDF_OCR import PDF_OCR
from TYPESET import TYPESET,open_file,UnZIP
from TRANSLATE import TRANSLATE

# =====子包需要的依赖，pyinstaller需要
import json,requests,random,openai,deepl,os
from hashlib import md5
from time import sleep,time

# 2025-02-26 16-55-36 腾讯，不需要了
# from tencentcloud.common import credential
# from tencentcloud.common.profile.client_profile import ClientProfile
# from tencentcloud.common.profile.http_profile import HttpProfile
# from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
# from tencentcloud.tmt.v20180321 import tmt_client, models

# =============================
print("这是一个利用服务商API自动全文翻译科技论文的python脚本。")
print("输入一个英文论文PDF，输出一个译文PDF（需安装有Latex）。详见README。")
print("——2025\n\n")

# 2025-03-07 15-49-31 直接上传PDF
texzipfile = PDF_OCR()

if texzipfile:
    basedir,filename=UnZIP(texzipfile)
else: # 打开本地zip文档
    print("未选择PDF……" ,end="")
    basedir,filename=open_file()

TYPESET(basedir,filename)

input("\n>> 检查无误后，按回车继续翻译...")

TRANSLATE(basedir,filename)

input("\n>> 按回车退出...")
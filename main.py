from TYPESET import TYPESET,open_file
from TRANSLATE import TRANSLATE

# =====子包需要的依赖，pyinstaller需要
import json,requests,random,openai,os
from hashlib import md5

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

# =============================
print("这是一个利用服务商API自动全文翻译科技论文的python脚本。")
print("输入的tex文件需要将文档PDF上传至mathpix识别后，导出latex下载。详见README。")
print("——2023\n\n")

basedir,filename=open_file()

TYPESET(basedir,filename)

input("<< 检查无误后，按回车继续翻译...")

TRANSLATE(basedir,filename)

input("<< 按任意键退出...")
import deepl,json
from time import sleep

# 文档：https://github.com/DeepLcom/deepl-python
# 安装：pip install --upgrade deepl

def create_client():
    print('deepL翻译为您服务')
    with open('translator_keys/deepl_keys.json') as f:
        keys=json.load(f)

    auth_key = keys['key']  # Replace with your key
    client = deepl.Translator(auth_key)
    return client

def translator(client,text):
    result = client.translate_text(text, target_lang="ZH")
    sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
    return result.text
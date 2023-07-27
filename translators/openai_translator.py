import openai,json
from time import sleep


def create_client():
    print('ChatGPT翻译为您服务')
    with open('translator_keys/openai_keys.json', 'r') as file:
        keys = json.load(file)
    openai.api_key = keys['key']
    return 0

def translator(client, text,  model='gpt-3.5-turbo'):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "Translate English latex text about plasma physics to Chinese latex text.Do not translate person's name.Be faithful or accurate in translation. Make the translation readable or intelligible. Be elegant or natural in translation.Do not add any additional text in the translation. Ensure that all percentage signs (%) are properly escaped"},
        #添加专有名词的翻译词典
        {"role": "system", "content": "- last closed surface:最外闭合磁面 "},
        {"role": "system", "content": "- kinetic:动理学 "},


        {"role": "user", "content": f" The text to be translated is:'{text}'\n"}
    	]
    )
    
    translation = response.choices[0].message.content.strip()
    sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
    return translation
import openai,json,yaml,os,logging,datetime
from time import sleep,time


# def create_client():
#     print('ChatGPT翻译为您服务')
#     with open('translator_keys/openai_keys.json', 'r') as file:
#         keys = json.load(file)
#     openai.api_key = keys['key']
#     return 0

# def translator(client, text,  model='gpt-3.5-turbo'):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#         {"role": "system", "content": "Translate English latex text about plasma physics to Chinese latex text.Do not translate person's name.Be faithful or accurate in translation. Make the translation readable or intelligible. Be elegant or natural in translation.Do not add any additional text in the translation. Ensure that all percentage signs (%) are properly escaped"},
#         #添加专有名词的翻译词典
#         {"role": "system", "content": "- last closed surface:最外闭合磁面 "},
#         {"role": "system", "content": "- kinetic:动理学 "},


#         {"role": "user", "content": f" The text to be translated is:'{text}'\n"}
#     	]
#     )
    
#     translation = response.choices[0].message.content.strip()
#     sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
#     return translation
def create_client():
    print("[**] OpenAI（还是啥的）为您服务！")
    class myclient(openai.OpenAI):
        def __init__(self):
            self.translator_name="openai"
            logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
            logging.warning("翻译器："+self.translator_name)
            
            # with open('translator_keys/openai_keys.json', 'r') as file:
            #     keys = json.load(file)
            with open('设置.yaml', 'r',encoding="utf8") as file: self.config=yaml.load(file,Loader=yaml.Loader)
            for apidir in self.config["翻译设置"]["翻译APIkeys文件夹"]:
                if os.path.exists(apidir):
                    print("[**] 读取API："+apidir+'/openai_keys.yaml')
                    break
            with open( apidir+'/openai_keys.yaml', 'r',encoding="utf8") as file:
                self.keys=yaml.load(file,Loader=yaml.Loader)    # 读取成一个dict
            
            super().__init__(api_key=self.keys["api_key"], base_url=self.keys["base_url"])
            
            # # 缓存术语表的功能，试一试 2025-02-21 10-03-37
            # with open("glossaries/fusion_glossary.csv",'r',  encoding='utf-8') as f:
            #     glsy=f.read()
            # response = openai.OpenAI(api_key=self.keys["api_key"], base_url=self.keys["context_api"]).chat.completions.create(
            #     model=self.keys["model"],
            #     messages=[
            #         {"role": "system", "content": "你将要翻译一系列科技论文，人名和缩写保持原装不翻译，下面是术语表，每行逗号前的英文对应逗号后的中文：\n"+glsy},
            #     ],
            #     mode="session",
            #     ttl=360,
            # )
            # self.contextid=response.id
            
            
            
        def asksth(self,text):
            response = self.chat.completions.create(
                model=self.keys["model"],
                messages=[
                    {"role": "user", "content": text},
                ],
                stream=False,
                max_tokens=4096,
                temperature=0.5,
            )
            resulttext=response.choices[0].message.content
            return resulttext
            
        def trans_text(self,text):
            return self.asksth("将下面这段latex格式论文文本翻译为中文（直接输出结果）："+text)
            
    
    return myclient()
            
            
        
    client = openai.OpenAI(api_key="72a0cb82-cd15-4243-a56a-908a3ad5bd1c", base_url="https://ark.cn-beijing.volces.com/api/v3")
    return client

# def translator(client,en):
#     response = client.chat.completions.create(
#     model="ep-20250217154024-g8vpz",
#         messages=[
#             {"role": "user", "content": "将下面这段latex格式文本翻译为中文（直接输出结果，无需额外的处理或解释）："+en},
#         ],
#         stream=False,
#         max_tokens=4096,
#         temperature=1.0,
#     )
#     resulttext=response.choices[0].message.content
#     return client, resulttext

if __name__=="__main__":
    tic=time()
    
    client=create_client()
    en="the kinetic theory in plasma physics"
    # en=r"The validity of the momentum equation is also much wider than the ideal MHD conditions would imply, although the reasons involve considerably more subtle physics. Recall that the collision dominated assumption is required to neglect $\boldsymbol{\Pi}_{i}$ and $\Pi_{e}$. In a collisionless plasma the magnetic field in a certain sense plays the role of collisions for the perpendicular motion; that is, perpendicular to the field, particles are confined to the vicinity of a given field line executing nearly (two-dimensional) isotropic motion if their gyro radius is much smaller than the characteristic plasma dimension. In fact, a calculation of $\boldsymbol{\Pi}_{\perp i}$ in the collisionless regime (see, for instance, Bowers and Haines (1971)) shows that for the MHD ordering $\Pi_{\perp i} / p_{i} \sim r_{L i} / a \ll 1$. Therefore, the perpendicular motion is fluid-like, implying that the perpendicular components of the momentum equation provide an excellent description of plasma behavior in either the collision dominated or collisionless regimes."
    en=r" Also shown in Fig. 3 are two additional cases that compare the variation of the shape at the two different elongations. The first case has the high elongation ( $\kappa=3$ ) of the TCV dee shape, but with higher triangularity ( $\delta=0.6$ ) and no squareness $(\lambda=0)$. Because of the poor coupling of equilibria with this shape to the TCV vacuum vessel, we use a conformal wall with the distance chosen ( $d=1.275 a$ ) to give the same value of $l_{i, 0}$ as the TCV dee configuration at zero pressure."
    
    zh = client.trans_text(en)
    print(zh)
    toc=time()
    print(f"耗时 {toc-tic:.4f} s")
# 需升级方舟 Python SDK到1.0.116版本或以上，pip install --upgrade 'volcengine-python-sdk[ark]'
from volcenginesdkarkruntime import Ark
from time import time
import yaml,datetime,logging,os

def create_client():
    print("[**] Doubao为您服务！")
    class myclient(Ark):
        def __init__(self):
            self.translator_name="doubao"
            logging.basicConfig(filename=f"log{datetime.datetime.now().strftime("%y%m")}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
            logging.warning("翻译器："+self.translator_name)
            
            # with open('translator_keys/openai_keys.json', 'r') as file:
            #     keys = json.load(file)
            with open('设置.yaml', 'r',encoding="utf8") as file: self.config=yaml.load(file,Loader=yaml.Loader)
            for apidir in self.config["翻译设置"]["翻译APIkeys文件夹"]:
                if os.path.exists(apidir):
                    print("[**] 读取API："+apidir+'/doubao_keys.yaml')
                    break
            with open(apidir+'/doubao_keys.yaml', 'r',encoding="utf8") as file: self.keys=yaml.load(file,Loader=yaml.Loader)    # 读取成一个dict
            
            super().__init__(api_key=self.keys["api_key"])
            
            # 2025-02-25 09-40-05 缓存模式
            # - "session" 能完整理解对话上下文，因此具备总结全文和AI问答的功能，代价是缓存调用量滚雪球，每次对话后越来越大
            # - "common_prefix" 只保留初始化时的前缀信息，每次对话时调用缓存大小不变，代价是不具备上下文理解能力
            cachemode = "session" if self.config["翻译设置"]["doubao-AI总结"] else "common_prefix" 
            
            # # 缓存术语表的功能，试一试 2025-02-21 10-03-37
            with open(f"glossaries/{self.config["翻译设置"]["doubao-要用的术语表"]}.csv",'r',  encoding='utf-8') as f:
                glsy=f.read()
            response = self.context.create(
                model=self.keys["model"],
                messages=[
                    {"role": "system", "content": "你将要翻译一篇科技论文，下面是术语表，每行逗号前的英文对应逗号后的中文：\n"+glsy},
                ],
                mode=cachemode,
                ttl=self.config["翻译设置"]["doubao-上下文超时时间"],
            )
            self.contextid=response.id
            print("[**] 已加载术语表："+self.config["翻译设置"]["doubao-要用的术语表"])
            
            with open("doubao-contextid.yaml","w",encoding="utf8") as f:
                tt={"cachemode":cachemode,
                    "expiretime":str(datetime.datetime.now()+datetime.timedelta(seconds=self.config["翻译设置"]["doubao-上下文超时时间"])),
                    "contextid":self.contextid}         
                yaml.dump(tt,f,allow_unicode=1)
              
            self.tokenup=0
            self.tokendown=0
            self.tokencache=0
            
            logging.basicConfig(filename="log.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
            logging.warning(".")
            logging.warning(".")
            logging.warning(f"doubao client已生成，contextid = {self.contextid}")
            
            
            
        def asksth(self,text):
            response = self.context.completions.create(
                model=self.keys["model"],
                messages=[
                    {"role": "user", "content": text},
                ],
                stream=False,
                max_tokens=4096,
                temperature=0.5,
                context_id=self.contextid,
            )
            resulttext=response.choices[0].message.content
            
            with open("doubao-contextid.yaml","r",encoding="utf8") as f: tt=yaml.load(f,Loader=yaml.Loader)  
            tt["expiretime"]=str(datetime.datetime.now()+datetime.timedelta(seconds=self.config["翻译设置"]["doubao-上下文超时时间"])) 
            with open("doubao-contextid.yaml","w",encoding="utf8") as f:  yaml.dump(tt,f,allow_unicode=1)
            
            self.tokenup += response.usage.prompt_tokens
            self.tokendown += response.usage.completion_tokens
            self.tokencache += response.usage.prompt_tokens_details.cached_tokens
            
            # self.check_usage()
            
            return resulttext
            
        def trans_text(self,text):
            return self.asksth("将下面这段latex格式论文文本翻译为中文（人名、单位和缩写不要翻译；直接输出结果，不要做额外的处理）："+text)
        
        def check_usage(self):
            thestr="消耗总token数：输入{:,}（外加命中缓存{:,}），输出{:,}，计费{}元"\
                .format(self.tokenup-self.tokencache, self.tokencache, self.tokendown, round((self.tokenup-self.tokencache)*1e-6*0.8+self.tokendown*1e-6*2+self.tokencache*1e-6*0.16,3))
            logging.warning(thestr)
            return "[*] "+thestr
            
    
    return myclient()

if __name__=="__main__":
    tic=time()
    
    client=create_client()
    # en="the kinetic theory in plasma physics"
    # en=r"The validity of the momentum equation is also much wider than the ideal MHD conditions would imply, although the reasons involve considerably more subtle physics. Recall that the collision dominated assumption is required to neglect $\boldsymbol{\Pi}_{i}$ and $\Pi_{e}$. In a collisionless plasma the magnetic field in a certain sense plays the role of collisions for the perpendicular motion; that is, perpendicular to the field, particles are confined to the vicinity of a given field line executing nearly (two-dimensional) isotropic motion if their gyro radius is much smaller than the characteristic plasma dimension. In fact, a calculation of $\boldsymbol{\Pi}_{\perp i}$ in the collisionless regime (see, for instance, Bowers and Haines (1971)) shows that for the MHD ordering $\Pi_{\perp i} / p_{i} \sim r_{L i} / a \ll 1$. Therefore, the perpendicular motion is fluid-like, implying that the perpendicular components of the momentum equation provide an excellent description of plasma behavior in either the collision dominated or collisionless regimes."
    en=r" Also shown in Fig. 3 are two additional cases that compare the variation of the shape at the two different elongations. The first case has the high elongation ( $\kappa=3$ ) of the TCV dee shape, but with higher triangularity ( $\delta=0.6$ ) and no squareness $(\lambda=0)$. Because of the poor coupling of equilibria with this shape to the TCV vacuum vessel, we use a conformal wall with the distance chosen ( $d=1.275 a$ ) to give the same value of $l_{i, 0}$ as the TCV dee configuration at zero pressure."
    # client,zh = translator(client,en)
    zh = client.trans_text(en)
    print(zh)
    
    toc=time()
    print(f"耗时 {toc-tic:.4f} s")
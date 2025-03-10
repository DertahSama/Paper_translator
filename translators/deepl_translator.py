from typing import Dict, Optional, Union
import deepl,json,yaml,os,logging,datetime
from time import sleep,time

# 文档：https://github.com/DeepLcom/deepl-python
# 安装：pip install --upgrade deepl



def create_client():
    print('[*] DeepL翻译为您服务')
    # with open('config.json',encoding='utf8') as f: config=json.load(f)
    # with open('translator_keys/deepl_keys.json') as f: keys=json.load(f)
    
    # glossary2use=config["翻译设置"]["deepL-要用的术语表"]#"fusion_glossary"  #要用的术语表
    # refreshThisGlossary=config['翻译设置']['deepL-更新术语表']       #是否要重新装载该术语表

    class myclient(deepl.Translator):
        def __init__(self):
            self.translator_name="deepl"
            logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
            logging.warning("翻译器："+self.translator_name)

            with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)
            for self.apidir in config["翻译设置"]["翻译APIkeys文件夹"]:
                if os.path.exists(self.apidir):
                    print("[**] 读取API："+self.apidir+'/deepl_keys.yaml')
                    break
            # with open('config.json',encoding='utf8') as f: config=json.load(f)
            with open(self.apidir+'/deepl_keys.yaml') as f: keys=yaml.load(f,Loader=yaml.Loader)
            
            glossary2use=config["翻译设置"]["deepL-要用的术语表"]#"fusion_glossary"  #要用的术语表
            refreshThisGlossary=config['翻译设置']['deepL-更新术语表']       #是否要重新装载该术语表
            
            anyAPIalive=False
            for idx in keys:
                if config['翻译设置']['deepL-重新检查账号额度']:
                    keys[idx]["state"]="on"  
                if keys[idx]["state"]=="on":
                    auth_key = keys[idx]['key']  # Replace with your key
                    self.activated_key_idx=idx
                    super().__init__(auth_key)  # 初始化母class，即加载deepl翻译器

                    usage=self.get_usage().character
                    usage_prct=round(usage.count/usage.limit*100,1)
                    self.charleft=usage.limit-usage.count
                    keys[idx]["used_percent"]=usage_prct
                    print(f"[*] 账号 {idx} 号已用额度：{usage_prct} %， {usage.count} / {usage.limit}",end="")

                    if config['翻译设置']['deepL-只检查账号额度']:
                        print("，继续检查下个额度……")
                        continue

                    if self.charleft<3000:
                        print("，继续尝试下一个弹匣……")
                        keys[idx]["state"]="off"
                        continue
                    

                    print("，启用中。")
                    anyAPIalive=True
                    
                    # 处理术语表
                    glossary_ready=False
                    glsrs = self.list_glossaries() # 当前API已有术语表
                    for glsy in glsrs:
                        if glsy.name == glossary2use:    # 当前API已经有这个术语表了
                            if refreshThisGlossary:
                                self.delete_glossary(glsy)
                            else:
                                self.current_glsy=glsy.glossary_id # 记录其id
                                print("[*] 已有并启用术语表： ",glsy.name)
                                glossary_ready=True
                            break

                    if not glossary_ready:    # 当面API没有这个术语表
                        with open(f'glossaries/{glossary2use}.csv', 'r',  encoding='utf-8') as csv_file: 
                            csv_data = csv_file.read()  # Read the file contents as a string
                            glsy = self.create_glossary_from_csv(
                                "fusion_glossary",
                                source_lang="EN",
                                target_lang="ZH",
                                csv_data=csv_data,
                            )
                            self.current_glsy=glsy.glossary_id # 记录其id
                            print("[*] 术语表已更新，并已启用：",glossary2use)
                    
                    break # 已成功装填API的break

            with open(self.apidir+'/deepl_keys.json','w+') as f: json.dump(keys,f,indent=4)

            if not anyAPIalive:
                raise AttributeError("[*] 所有DeepL密钥的额度都已不足！")
            


        def trans_text(self,text):
            self.charleft -= len(text) # 剩余额度扣除本次的字符数
            # print(client.charleft)
            
            if (self.charleft)<3000:
                print("[*] 换弹匣……")
                self.__init__()
            
            if len(text)>2:
                result = self.translate_text(text,source_lang="EN", target_lang="ZH-Hans",preserve_formatting=True,glossary=self.current_glsy)
                resulttext=result.text
                sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
            else:
                resulttext=''
            # usage=client.get_usage().character
            # print(usage.limit-usage.count)
            return resulttext
        
        def check_usage(self):
            with open(self.apidir+'/deepl_keys.json') as f: keys=json.load(f)

            usage=self.get_usage().character
            usage_prct=round(usage.count/usage.limit*100,1)
            self.charleft=usage.limit-usage.count
            keys[self.activated_key_idx]["used_percent"]=usage_prct
            print(f"[*] 账号 {self.activated_key_idx} 号已用额度：{usage_prct} %， {usage.count} / {usage.limit}")

            with open(self.apidir+'/deepl_keys.json','w+') as f: json.dump(keys,f,indent=4)


        

    # anyAPIalive=False
    # for idx in keys:
    #     if config['翻译设置']['deepL-重新检查账号额度']:
    #         keys[idx]["state"]="on"  # 【可操作】解除该行的注释来手动刷新API的状态
    #     if keys[idx]["state"]=="on":
    #         auth_key = keys[idx]['key']  # Replace with your key
            # client = deepl.Translator(auth_key)

    #         usage=client.get_usage().character
    #         usage_prct=round(usage.count/usage.limit*100,1)
    #         client.charleft=usage.limit-usage.count
    #         keys[idx]["used_percent"]=usage_prct
    #         print(f"[*] 账号 {idx} 号已用额度：{usage_prct} %， {usage.count} / {usage.limit}",end="")

    #         if client.charleft<3000:
    #             print("，继续尝试下一个弹匣……")
    #             keys[idx]["state"]="off"
    #             continue
            
    #         print("，启用中。")
    #         anyAPIalive=True
            
    #         # 处理术语表
    #         glossary_ready=False
    #         glsrs = client.list_glossaries() # 当前API已有术语表
    #         for glsy in glsrs:
    #             if glsy.name == glossary2use:    # 当前API已经有这个术语表了
    #                 if refreshThisGlossary:
    #                     client.delete_glossary(glsy)
    #                 else:
    #                     client.current_glsy=glsy.glossary_id # 记录其id
    #                     print("[*] 已有并启用术语表： ",glsy.name)
    #                     glossary_ready=True
    #                 break

    #         if not glossary_ready:    # 当面API没有这个术语表
    #             with open(f'glossaries/{glossary2use}.csv', 'r',  encoding='utf-8') as csv_file: 
    #                 csv_data = csv_file.read()  # Read the file contents as a string
    #                 glsy = client.create_glossary_from_csv(
    #                     "fusion_glossary",
    #                     source_lang="EN",
    #                     target_lang="ZH",
    #                     csv_data=csv_data,
    #                 )
    #                 client.current_glsy=glsy.glossary_id # 记录其id
    #                 print("[*] 术语表已更新，并已启用：",glossary2use)
            
    #         break # 已成功装填API的break

    # with open('translator_keys/deepl_keys.json','w+') as f:
    #     json.dump(keys,f,indent=4)
    
    # if not anyAPIalive:
    #     raise AttributeError("[*] 所有DeepL密钥的额度都已不足！")

    # usage=client.get_usage().character
    # usage_prct=round(usage.count/usage.limit*100,1)
    # print(f"[*] 当前DeepL账号已用额度：{usage_prct} %， {usage.count} / {usage.limit}")

    # if (usage.limit-usage.count)<3000:
    #     keys[idx]["state"]="off"


    return myclient()

def translator(client,text):
    client.charleft -= len(text) # 剩余额度扣除本次的字符数
    # print(client.charleft)
    
    if (client.charleft)<3000:
        print("[*] 换弹匣……")
        client=create_client()
    
    if len(text)>2:
        result = client.translate_text(text,source_lang="EN", target_lang="ZH",preserve_formatting=True,glossary=client.current_glsy)
        resulttext=result.text
        sleep(0.2) # 每秒最多请求5次，可以删掉这行来搞快点
    else:
        resulttext=''
    # usage=client.get_usage().character
    # print(usage.limit-usage.count)
    return client, resulttext

if __name__=="__main__":
    client=create_client()
    # en=r"The validity of the momentum equation is also much wider than the ideal MHD conditions would imply, although the reasons involve considerably more subtle physics. Recall that the collision dominated assumption is required to neglect $\boldsymbol{\Pi}_{i}$ and $\Pi_{e}$. In a collisionless plasma the magnetic field in a certain sense plays the role of collisions for the perpendicular motion; that is, perpendicular to the field, particles are confined to the vicinity of a given field line executing nearly (two-dimensional) isotropic motion if their gyro radius is much smaller than the characteristic plasma dimension. In fact, a calculation of $\boldsymbol{\Pi}_{\perp i}$ in the collisionless regime (see, for instance, Bowers and Haines (1971)) shows that for the MHD ordering $\Pi_{\perp i} / p_{i} \sim r_{L i} / a \ll 1$. Therefore, the perpendicular motion is fluid-like, implying that the perpendicular components of the momentum equation provide an excellent description of plasma behavior in either the collision dominated or collisionless regimes."
    en=r" Also shown in Fig. 3 are two additional cases that compare the variation of the shape at the two different elongations. The first case has the high elongation ( $\kappa=3$ ) of the TCV dee shape, but with higher triangularity ( $\delta=0.6$ ) and no squareness $(\lambda=0)$. Bessel functions is in the notation of G. N. Watson (1922). $a = 3\mathrm{m}^{-3}, b=16\mathrm{Wb}$.  "
    zh=client.trans_text(en)
    # client, zh=translator(client,en)
    print(zh)
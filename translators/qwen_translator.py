import openai,json,yaml,os,logging,datetime
from time import sleep,time


def create_client():
    print("[**] Qwen为您服务！")
    class myclient(openai.OpenAI):
        def __init__(self):
            self.translator_name="qwen"
            logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
            logging.warning("翻译器："+self.translator_name)
            
            # with open('translator_keys/openai_keys.json', 'r') as file:
            #     keys = json.load(file)
            with open('设置.yaml', 'r',encoding="utf8") as file: self.config=yaml.load(file,Loader=yaml.Loader)
            for apidir in self.config["翻译设置"]["翻译APIkeys文件夹"]:
                if os.path.exists(apidir):
                    print("[**] 读取API："+apidir+'/qwen_keys.yaml')
                    break
            with open( apidir+'/qwen_keys.yaml', 'r',encoding="utf8") as file:
                self.keys=yaml.load(file,Loader=yaml.Loader)    # 读取成一个dict
            
            if not self.keys["api_key"]:
                print("[error] 你还没填写翻译器API keys！请到 {apidir}/ 中填写。若还没有API，申请方法请见README!")
                logging.error("[error]未找到翻译器API keys")
                input("按回车退出……")
                exit()

            super().__init__(api_key=self.keys["api_key"], base_url=self.keys["base_url"])
            

            
        def trans_text(self,text):
            
            with open("glossaries/fusion_glossary_distill.csv",'r',encoding="utf8") as f:
            # with open("glossaries/void.csv",'r',encoding="utf8") as f:
                glsy=f.readlines()

            glsylist=[]
            for l in glsy:
                cut=l.strip().split(",")
                glsylist.append({"source":cut[0],"target":cut[1]})
                
            
            translation_options = {
                "source_lang": "English",
                "target_lang": "Chinese"
            }
            translation_options["terms"]=glsylist
            
            response = self.chat.completions.create(
                model="qwen-mt-turbo",
                messages=[
                    {"role": "user", "content": text},
                ],
                extra_body={
                    "translation_options": translation_options
                }
            )
            resulttext=response.choices[0].message.content
            
            print(response)
            return resulttext
            
        # def trans_text(self,text):
        #     return self.asksth("将下面这段latex格式论文文本翻译为中文（直接输出结果）："+text)
            
    
    return myclient()
            

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
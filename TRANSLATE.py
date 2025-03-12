import os,json,yaml,datetime,asyncio,logging
from tkinter import filedialog
from time import time

def open_file():
    # ========打开文件=========
    # with open('config.json',encoding='utf8') as f:
    #     config=json.load(f)
    with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)

    if config["翻译设置"]["处理filepath里储存的文件名"]:
        with open('filepath.txt', encoding='utf-8') as f:
            file=json.load(f)
        basedir=file["basedir"]
        filename=file["filename"]
        print("[*] 正在处理: "+basedir+r'/'+filename)
    else:
        print(">> 请打开从Mathpix导出的tex文档...")
        f_path = filedialog.askopenfilename(initialdir='./',filetypes=(('tex files','*.tex'),))
        if not f_path:
            exit()
        (basedir,filename)=os.path.split(f_path)
        print("[*] 正在处理: "+basedir+r'/'+filename)
        
        with open('filepath.txt', 'w', encoding='utf-8') as f:
            json.dump({'basedir':basedir,'filename':filename},f,indent=4, ensure_ascii=False)

    return basedir,filename

def TRANSLATE(basedir,filename):
    # with open('config.json',encoding='utf8') as f: config=json.load(f)
    with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)

    input_file_path = basedir+'/[排版]'+filename
    output_file_path = basedir+'/[翻译]'+filename

    with open(input_file_path, 'r',encoding='utf-8') as file_2:
        tex_2 = file_2.readlines()
    with open(basedir+"/suffix.txt",'r',encoding='utf-8') as f:
        suffix=f.read()

    # ================== 加载翻译器 =================
    import translate_func2 as tf
    from importlib import import_module

    translatorsdict={"1":"baidu","2":"tencent","3":"openai","4":"deepl","5":"doubao","5.1":"doubao_async","9":"test","0":"count_num"}
    if config["翻译设置"]["默认翻译器"] in  ("1","2","3","4","5","5.1","9","0"):
        s=config["翻译设置"]["默认翻译器"]
        print(f"[**] 已默认选择 {s}:{translatorsdict[s]} 进行翻译……")
    else:
        s=input(">> 选择翻译器"+str(translatorsdict)+"：")
    
    
    # s="4"
    # print("使用DeepL进行翻译……")

    # exec("import translators."+translatorsdict[s]+"_translator as tt ") # 感觉不太优雅，但是就这样吧！
    tt=import_module("translators."+translatorsdict[s]+"_translator")

    client=tt.create_client()


    # ================== 进行翻译 ===================
    tic=time()
    tex_3 = tex_2.copy()
    tex_3 = tf.translate_title(client,tex_3)
    # tex_3 = tf.translate_body(client,tex_3,suffix)
    tex_3 = asyncio.run(  tf.translate_body1(client,tex_3,suffix)  ) # 2025-02-27 20-28-43 升级为异步并发 2025-02-27 22-40-17 将list的翻译整合其中
    
    # tex_3 = tf.translate_list(client,tex_3)    # 翻译itemize和enumerate环境 @231110新增
    # tex_3 = asyncio.run(  tf.translate_list1(client,tex_3)  ) # 2025-02-27 22-05-24 升级为异步并发
    
    # if client.translator_name in ("doubao",):
    #     print(client.check_usage())
        # print(f"[*] 消耗总token数：输入{client.tokenup-client.tokencache}（外加缓存{client.tokencache}），输出{client.tokendown}，计费{round((client.tokenup-client.tokencache)*1e-6*0.8+client.tokendown*1e-6*2+client.tokencache*1e-6*0.16,3)}元")
    
    
    if client.translator_name == "doubao" and config["翻译设置"]["doubao-AI总结"] :
        import typeset_func2 as lf
        with open('template.tex', 'r',encoding='utf-8') as file_1:
            tex_template = file_1.readlines()
        format_AIsum = lf.get_format_AIsummary(tex_template)
        
        tex_3 = tf.AIsummary(client,tex_3,format_AIsum)
    
    # 用量检查
    if client.translator_name in ("deepl",):
        client.check_usage() 
    if client.translator_name in ("doubao","doubao_async",):
        print(client.check_usage())
    if client.translator_name == "count_num" :
        print(f"\n[*] 总字符数：{client.charnum}，总token数（供参考）：{client.tokennum}")
        

    tex_3=tf.post_decoration(tex_3)
    
    # ====== 保存 ======
    basedir=basedir.replace("\\","/")
    output_file_path=output_file_path.replace("\\","/")
    
    if not client.translator_name == "count_char_num" :
        with open(output_file_path, 'w',encoding='utf-8') as file_3:
            file_3.write(' '.join(tex_3))
            
    if config['翻译设置']['立即编译所得tex']:
        print("\n[*] 编译排版后的tex文件中……")
        
        cmd=f'cd /d \"{basedir}\" '\
            '&& '\
            f'xelatex.exe -synctex=1 -interaction=batchmode -halt-on-error '\
            f'\"{output_file_path}\"' 
            # ' > /dev/null'
        os.system(cmd)
        print("[*] 已编译为PDF文件\n")
        logging.warning("[翻译]已编译为PDF文件")
        os.startfile(output_file_path.replace(r'\\','/').replace('.tex','.pdf'))

    
    toc=time()
    print(f"[*] 翻译耗时 {toc-tic:.4f} s")
    logging.warning(f"翻译耗时 {toc-tic:.4f} s")
    
    print(">> 已保存到："+output_file_path)
    # path1=output_file_path.replace('/','\\')
    # os.system(f'C:/Windows/explorer.exe /select, "{path1}"')
    
    # ====== doubao-AI问答 ======
    if config["翻译设置"]["doubao-AI总结"] and client.translator_name == "doubao":
        a=input(">> 要就这篇文章展开AI问答吗？（y开始/回车退出）：")
        print("[**] 退出后你仍可以运行「doubao_AItalk.py」来继续对话哦！")
        if a=="y":
            from doubao_AItalk import AItalk
            AItalk()
            
            # while 1:
            #     print("")
            #     askkk=input("（输入xxx来退出）>>")
            #     if askkk=="xxx": break
            #     with open(basedir+r"\AI问答.md","a+",encoding="utf8") as f:
            #         f.writelines("\n\n.\n-------\n# "+datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")+"\n")
            #         f.writelines("> "+askkk+"\n\n")
            #         rsp=client.asksth(askkk)
            #         f.writelines(rsp)
            #     print(rsp)
                    
            

    # os.remove('filepath.txt')
    # os.remove('suffix.txt')

if __name__=="__main__":
    basedir,filename=open_file()
    logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
    logging.warning(".")
    logging.warning(".")
    TRANSLATE(basedir,filename)

"""
翻译器在translators文件夹中，通过修改下面import哪个文件来决定用那个翻译库。
这些翻译库都需要自备api。
支持的服务商：
openai（chatGPT3.5），deepl，baidu，tencent
"""

# translatorsdict={"1":"baidu","2":"tencent","3":"openai","4":"deepl","5":"test","0":"count_char_num"}
# s=input("<< 选择翻译器"+str(translatorsdict)+"：")

# # tt=__import__(translatorsdict[s]+"_translator")
# exec("import translators."+translatorsdict[s]+"_translator as tt ") # 感觉不太优雅，但是就这样吧！
# # from baidu_translator import * 


import re,sys,asyncio
from time import sleep

def FindFirst(pat: str, lst: list[str], flg: str=0) -> int:  #找到字符串数组lst中第一次正则匹配到pat的索引位置
    '''
    找到字符串数组lst中第一次正则匹配到pat的序号。若未找到则返回None。
    :param pat: 正则匹配表达式
    :param lst: 元素为字符串的数组
    :param flg: 是`re.search()`的`flags`参数。默认为0，常用的是忽略大小写的`re.I`
    :return:    若找到，返回索引号；若未找到，返回None
    '''
    try:
        return lst.index(next(filter(re.compile(pat,flags=flg).search,lst)))
    except StopIteration: # 一次也next不出来，说明没有
        return None


def ProgressBar(now : int, alls : int):
    '''
    根据输入的当前值和总数值打印一个进度条。100%前不换行，下一次打印时将覆盖本行；100%后换行。
    :param now:     当前值
    :param alls:    总数值
    '''
    progress=int(now/alls*50)
    print("\r进度: %d/%d: "%(now,alls), "▋"*progress + "-"*(50-progress), end="")
    if now==alls:
        print("done！")   #100%了换个行
    sys.stdout.flush()
    sleep(0.001)
    
def ProgressBar_par(N=[]):
    # 适用于各种并发的进度条
    if isinstance(N,int):
        with open("pbar.txt","w") as f:
            f.write(f"{N}\n")
    elif N==[]:
        with open("pbar.txt","r+") as f:
            c=f.readline()
            alls=int(c)
            
            now=f.readlines()
            f.write("1\n")
            now=len(now)+1
            
            progress=int(now/alls*50)
            print("\r并行进度: %d/%d: "%(now,alls), "▋"*progress + "-"*(50-progress), end="")
            if now==alls:
                print("done！")   #100%了换个行
            sys.stdout.flush()
            sleep(0.001)
    else:
        raise Exception("要么输入总数N来初始化，要么什么都不输入来显示进度！")

def translate_text(client, text: str) -> str:
    

    if not (client.translator_name in ("openai","doubao","doubao_aysnc")):  # 用大模型的不用替换
        # 设置原文中要强制保持原样的部分
        to_reserve=[r'(?:\$.*?\$)',         # 行内公式 
                    r'(?:\\cverb\|.*?\|)',
                    r'\\\w+(?:\{.*?\})*', # 任意latex命令
                    ]
        reserved_results = re.findall(r'(?:(?:' + '|'.join(to_reserve) + r') *)+' ,text)
        # print(inline_eqn_results)
        marker=lambda i: ' [x'+'%02d'%i+'] '  # 替换为保留符marker，例如[#03]
        # marker=lambda i: '【'+chr(0x4E00+i)+'】'  # 替换为保留符marker，例如[#03]
        for i in range(len(reserved_results)):
            # inline_eqn=reserved_results[i]
            # marker='xx'+'%02d'%i  # 把行内公式替换成标记，防止翻译时丢符号
            # marker='[#'+'%02d'%i+']'  # 把行内公式替换成标记，防止翻译时丢符号
            text = text.replace(reserved_results[i],marker(i))
    
    to_convert=[[r'\&',r'&'],
            [r'\%',r'%'],
            [r'\#',r'#']]
    for apair in to_convert:
        text = text.replace(apair[0],apair[1])
    
    text = re.sub(r'(Chaps?|Secs?|Eqn?s?|Refs?|Figs?)\. ?(\(?\d+\)?)',r'\1\2',text,flags=re.IGNORECASE)  # 把诸如「Sec. 3」变成「Sec3」，防止这个点被认成句号导致错误断句。

    if client.translator_name in ("doubao_async",):
        text_zh:str = asyncio.run(client.trans_text(text.strip()))
    else:
        text_zh:str = client.trans_text(text.strip())
        
    
    
    text_zh = text_zh.replace('＃','#').replace('｛',r'{').replace('｝',r'}')  # 谁能想到deepl会随机把半角#替换成全角＃？？？
    
    for apair in to_convert:
        text_zh = text_zh.replace(apair[1],apair[0])
    
    if not (client.translator_name in ("openai","doubao","doubao_aysnc")):  # 用大模型的不用替换
        for i in range(len(reserved_results)):
            # inline_eqn=reserved_results[i]
            # marker='xx'+'%02d'%i
            text_zh = text_zh.replace(marker(i).strip(),reserved_results[i]) # 替换回来

    
    return client, text_zh


    

def translate_title(client,tex_file):
    st = r'\\begin{abstract}'
    st1 = r'\\title\{(.*?)\}'
    print('[**] 翻译标题……')

    # client=tt.create_client()

    title_idx=FindFirst(st1,tex_file)
    if title_idx:
        title_en=re.search(st1,tex_file[title_idx]).group(1)
        client, title_zh=translate_text(client,title_en)
        tex_file[title_idx]=r'\title{'+title_zh+r'\\ \Large{'+title_en+'}}'
        print("标题：",title_zh)
    else:
        print("no title found!")

    # abstract_idx=FindFirst(st,tex_file)
    # if abstract_idx:
    #     abstract_idx+=1
    #     abstract_en = tex_file[abstract_idx]
    #     client, abstract_zh = translate_text(client,abstract_en)
    #     abstract_zh += '\n'
    #     tex_file[abstract_idx] = r'{'+abstract_zh+r'}\\ \indent '+abstract_en
    # else:
    #     print("no abstract found!")
    
    return tex_file


async def taowa(client,line,sema):
    async with sema:
        
        to_convert=[[r'\&',r'&'],
                    [r'\%',r'%'],
                    [r'\#',r'#']]
        for apair in to_convert:
            line = line.replace(apair[0],apair[1])
            
        rline = await client.trans_text(line)
        
        for apair in to_convert:
            rline = rline.replace(apair[1],apair[0])
        
        ProgressBar_par()
        return rline
        
        
async def translate_body1(client, tex_file :list[str], suffix:list[str]) -> list[str]:
   # 2025-02-27 19-39-55 改造为适应异步并发
    print('[**] 翻译正文……')
    start_idx=FindFirst("==document boby begins",tex_file)
    if not start_idx:
        start_idx=FindFirst(r"\\begin{document}",tex_file)
    end_idx=FindFirst("==document body ends",tex_file)
    if not end_idx:
        end_idx=FindFirst(r"\\end{document}",tex_file)
        tex_file[end_idx]='\n'
        tex_file.extend(['\n','\\end{document}\n'])
    
    flag = 0
    L = end_idx-start_idx+1
    
    # 把需要翻译的东西提取出来
    data_abst=[]  # 摘要
    data_bulk=[]  # 正文
    data_titl=[]  # 章节标题
    data_capt=[]  # 图注
    
    # ==== 摘要部分 ====
    
    st = r'\\begin{abstract}'

    abstract_idx=FindFirst(st,tex_file)
    if abstract_idx:
        abstract_idx+=1
        abstract_en = tex_file[abstract_idx]
        data_abst.append([abstract_idx, abstract_en])
    else:
        print("no abstract found!")
    
    
    # ==== 正文部分 ====
    for line_idx in range(start_idx+1,end_idx):
        line = tex_file[line_idx].strip()
        if re.search(r"^ *%.*",line):   # 注释行直接跳过
            continue

        flag += len(re.findall(r'\\begin{.*?}',line))  #子环境层数

        if flag==0 and len(line)>2: # 非子环境内
            searchobj=re.search(r'\\(part|chapter|section|subsection|subsubsection|paragraph)\*?\{(.*)\}',line) # 搜寻章节标题
            if searchobj: # 章节标题的处理
                titl_en=searchobj.group(2).strip()
                if len(titl_en)>2: # 长度达到最小限制3个字母，才翻译
                    data_titl.append([line_idx, titl_en])
                else:
                    print(f"[**]警告：第{line_idx+start_idx-1}行的标题过短，可能有误，请检查。")

            elif re.search(r'^%',line.strip()): # 注释行，什么也不做
                pass
            else: # 普通正文的处理
                data_bulk.append([line_idx,line])

        if not flag==0: # 子环境内
            mo = re.search(r'\\caption{(.*)}',line) # 翻译图注
            if mo:
                caption_en=mo.group(1).strip()
                if len(caption_en)>2:
                    data_capt.append([line_idx,caption_en])
                else:
                    print(f"[**]警告：第{line_idx+start_idx-1}行的题注过短，可能有误，请检查。")
        
        flag -= len(re.findall(r'\\end{.*?}',line))
    
    N0=len(data_abst)
    N1=len(data_bulk)
    N2=len(data_capt)
    N3=len(data_titl)
    
    # 合一
    data = data_abst + data_bulk + data_capt + data_titl 
    all_en = [item[1] for item in data]
    
    # ===== 列表部分也放在这里一齐干了吧！ =====
    
    total_num=len(re.findall(r'\\begin\{(?:itemize|enumerate)\}',' '.join(tex_file)))
    if total_num == 0:
        data_list=[]      # [list_start_idx,list_end_idx,a_list_en]
        data_listline=[]  # [list_start_idx, list_idx, text_en, r'  \item ']
        all_en_list=[]
    else:
        data_list=[]      # [list_start_idx,list_end_idx,a_list_en]
        data_listline=[]  # [list_start_idx, list_idx, text_en, r'  \item ']
        
        # ==== 找到所有列表 ====
        line_idx=start_idx
        while not ("==document body ends" in tex_file[line_idx] or r"\end{document}" in tex_file[line_idx]):
            line=tex_file[line_idx]
            if ("== DO NOT TRANSLATE" in line):
                pass
            if re.search(r'\\begin\{(?:itemize|enumerate)\}',line) and not ("== DO NOT TRANSLATE" in line):
                list_start_idx=line_idx
                list_end_idx=FindFirst(r'\\end\{(?:itemize|enumerate)\}',tex_file[list_start_idx:])+list_start_idx

                a_list_en=tex_file[list_start_idx:list_end_idx+1].copy()
                data_list.append([list_start_idx,list_end_idx,a_list_en])
                
                # a_list_zh=a_list_en.copy()
                flag=0

                for list_idx,list_line in enumerate(a_list_en):
                    if list_idx==0 or list_idx==len(a_list_en)-1:
                        continue # 首行和尾行是列表环境定义，不处理  
                    searchobj=re.search(r'\\item (.*)',list_line) # 找个item
                    if searchobj: # 确保item行格式正确
                        text_en=searchobj.group(1)
                        data_listline.append([list_start_idx, list_idx, text_en, r'  \item '])
                        # client, text_zh = translate_text(client, text_en)
                        # a_list_zh[list_idx]=r'  \item '+text_zh+'\n' 
                    else: # 其它行就随缘吧
                        flag+=len(re.findall(r'\\begin{.*}',list_line))  #子环境层数
                        if not flag:
                            text_en=list_line
                            data_listline.append([list_start_idx, list_idx, text_en, r''])
                            # client, text_zh = translate_text(client, text_en)
                            # a_list_zh[list_idx]=text_zh+'\n'
                        flag-=len(re.findall(r'\\end{.*}',list_line))


                together=['\\enzhbox{\n',] + a_list_en + ['\n}{\n',] + a_list_en + ['\n}\n',]
                # tex_file=tex_file[:list_start_idx] + together + tex_file[list_end_idx+1:]
                line_idx=list_end_idx+1
            else:
                line_idx+=1
        
        Nlist=len(data_listline)
        all_en_list=[item[2] for item in data_listline]
    
    
    
    
    
    all_en = all_en + all_en_list
    
    
    NN=len(all_en)
    
    # ====== 一齐翻译 ======
    if client.translator_name == "doubao_async":
        ProgressBar_par(NN)
        # 控制同时进行的异步任务的数量，原理不明
        sema = asyncio.Semaphore(100) 
        
        tasks = [  asyncio.create_task( taowa(client,en,sema) )  for en in all_en  ]
        zhdata = await asyncio.gather(*tasks) 
    else:
        # tasks = [  client.trans_text(item[1])  for item in data  ]
        # zhdata = list(tasks)
        zhdata=[]
        for i in range(NN):
            client, line_zh = translate_text(client, all_en[i])
            zhdata.append(line_zh)
            ProgressBar(i+1,NN)
    
    # 切分
    zhdata_abst=zhdata[:N0]
    zhdata_bulk=zhdata[N0:N0+N1]
    zhdata_capt=zhdata[(N0+N1):(N0+N1+N2)]
    zhdata_titl=zhdata[(N0+N1+N2):(N0+N1+N2+N3)]
    zhdata_list=zhdata[(N0+N1+N2+N3):]
    
    # ==== 把翻译好的东西放回去 ====
    for i,abstzh in enumerate(zhdata_abst):  # 摘要
        line_idx = data_abst[i][0]
        absten = data_abst[i][1]
        tex_file[abstract_idx] = r'{'+abstzh+r'}\\ \indent '+absten
    
    for i,linezh in enumerate(zhdata_bulk):  # 正文
        line_idx = data_bulk[i][0]
        line = data_bulk[i][1]
        head =r'\noindent ' if re.search(r'^ ?[a-z]',line) else ''
        tex_file[line_idx] = "\n"+r"\enzhbox{  "+head+line+"}{\n"+head+linezh+"}\n"
    
    for i,captzh in enumerate(zhdata_capt):  # 图注
        line_idx = data_capt[i][0]
        capt = data_capt[i][1]
        tex_file[line_idx]=r"\caption{\uline{"+capt+ r"}\\" + captzh + "}\n"
            
    for i,titlzh in enumerate(zhdata_titl):  # 章节标题
        line_idx = data_titl[i][0]
        titl = data_titl[i][1]
        line = tex_file[line_idx].strip()
        tex_file[line_idx] = line.replace(titl,titlzh)+'\n {  \\small '+titl+' \\par }\n'
    
    bias=0
    for thislist in data_list:              # 列表
        list_start_idx = thislist[0]
        list_end_idx   = thislist[1]
        list_en        = thislist[2]
        
        idx4thislist = [ i for i,item in enumerate(data_listline) if item[0]==list_start_idx ]  # 挑出data_listline中属于thislist的lines
        listidx4thislist =[ data_listline[j][1] for j in idx4thislist ]  # thislist中的行号
        linezh4thislist = [ zhdata_list[j]      for j in idx4thislist ]  # 对应thislist行号的译文
        linepfx4thislist =[ data_listline[j][3] for j in idx4thislist ]  # 前缀（「\item」或者空）
        
        list_zh=list_en.copy()
        for k,list_idx in enumerate(listidx4thislist):
            list_zh[list_idx] = linepfx4thislist[k] + linezh4thislist[k] + "\n"  # list_zh中对应行号的文本改成译文

        together=['\\enzhbox{\n',] + list_en + ['\n}{\n',] + list_zh + ['\n}\n',]
        tex_file=tex_file[: list_start_idx+bias ] + together + tex_file[ list_end_idx+bias+1 :]
        
        bias += len(together)-(list_end_idx-list_start_idx+1)
    
    
    
    
    
    end_idx=FindFirst("==document body ends",tex_file)   
    tex_file[end_idx+1]=suffix # 接回尾巴
    
    # print('[*] 更新API状态……')
    # client=tt.create_client()
    return tex_file
            
        
    
    
    
    
    
    
    

def translate_body(client, tex_file :list[str], suffix:list[str]) -> list[str]:
   
    print('[**] 翻译正文……')

    # client=tt.create_client()
    # def doit(mo): # 图注翻译替换函数
    #     text_en=mo.group(1)
    #     client, text_ch=translate_text(client,text_en)
    #     text_ch="\\caption{\\uline{"+text_en+ "}\\\\" + text_ch + "}"
    #     return text_ch

    start_idx=FindFirst("==document boby begins",tex_file)
    if not start_idx:
        start_idx=FindFirst(r"\\begin{document}",tex_file)
    end_idx=FindFirst("==document body ends",tex_file)
    if not end_idx:
        end_idx=FindFirst(r"\\end{document}",tex_file)
        tex_file[end_idx]='\n'
        tex_file.extend(['\n','\\end{document}\n'])
    
    flag = 0
    L = end_idx-start_idx+1
    for line_idx in range(start_idx+1,end_idx):
        line = tex_file[line_idx].strip()
        if re.search(r"^ *%.*",line):   # 注释行直接跳过
            continue
        if not (client.translator_name == "count_char_num"):
            ProgressBar(line_idx-start_idx+1,L-1)
        # print(line_idx-start_idx+1,'/',L)

        flag += len(re.findall(r'\\begin{.*?}',line))  #子环境层数

        if flag==0 and len(line)>2: # 非子环境内
            searchobj=re.search(r'\\(part|chapter|section|subsection|subsubsection|paragraph)\*?\{(.*)\}',line) # 搜寻章节标题
            if searchobj: # 章节标题的处理
                titl_en=searchobj.group(2).strip()
                if len(titl_en)>2: # 长度达到最小限制3个字母，才翻译
                    client, name_ch=translate_text(client, titl_en)
                    line_ch=line.replace(titl_en,name_ch)+'\n {  \\small '+titl_en+' \\par }\n'
                else:
                    print(f"[**]警告：第{line_idx+start_idx-1}行的标题过短，可能有误，请检查。")
                    line_ch=line
                tex_file[line_idx] = line_ch
            elif re.search(r'^%',line.strip()): # 注释行，什么也不做
                pass
            else: # 普通正文的处理
                head =r'\noindent ' if re.search(r'^ ?[a-z]',line) else '' #如果是小写字母开头，即不缩进
                client, line_ch = translate_text(client, line)
                # line_ch=line_ch.replace("%","\\%")
                # tex_file[line_idx] = r"\begin{leftbar} \small "+line+r"\end{leftbar}"+line_ch # 翻译后，在前面放上原文
                # tex_file[line_idx] = "\n"+r"\begin{supertabu} to 1\linewidth [t]{|X[l]|X[l]} \small "+line+r"&"+line_ch+r"\end{tabu} \medskip" # 翻译后，在前面放上原文
                tex_file[line_idx] = "\n"+r"\enzhbox{  "+head+line+"}{\n"+head+line_ch+"}\n"

        if not flag==0: # 子环境内
            mo = re.search(r'\\caption{(.*)}',line) # 翻译图注
            if mo:
                caption_en=mo.group(1).strip()
                if len(caption_en)>2:
                    client, caption_zh = translate_text(client,caption_en)
                else:
                    print(f"[**]警告：第{line_idx+start_idx-1}行的题注过短，可能有误，请检查。")
                    caption_zh=""
                tex_file[line_idx]="\\caption{\\uline{"+caption_en+ "}\\\\" + caption_zh + "}\n"#re.sub(r'\\caption{(.*)}',doit,line) 
        
        flag -= len(re.findall(r'\\end{.*?}',line))

    tex_file[end_idx+1]=suffix # 接回尾巴
    
    # print('[*] 更新API状态……')
    # client=tt.create_client()
    return tex_file

# def translate_captions(tex_file):
#     print('Translating captions')
#     client=tt.create_client()
#     def doit(mo):
#         text_en=mo.group(1)
#         text_ch=translate_text(client,text_en)
#         text_ch="\\caption{"+text_en+ "\\\\" + text_ch + "}"
#         return text_ch
    
#     L=len(tex_file)
#     for line_idx, line in enumerate(tex_file):
#         ProgressBar(line_idx+1,L)
#         tex_file[line_idx]=re.sub(r'\\caption{(.*)}',doit,line)

    # return tex_file

async def translate_list1(client,tex_file):
    # 2025-02-27 21-39-35 异步并行改造
    print('[**] 翻译itemize和enumerate环境……')

    start_idx=FindFirst("==document boby begins",tex_file)
    if not start_idx:
        start_idx=FindFirst(r"\\begin{document}",tex_file)
    
    line_idx=start_idx
    count=0
    total_num=len(re.findall(r'\\begin\{(?:itemize|enumerate)\}',' '.join(tex_file)))
    if total_num==0:
        print("未找到，已完成。")
        return tex_file
    
    data_list=[]      # [list_start_idx,list_end_idx,a_list_en]
    data_listline=[]  # [list_start_idx, list_idx, text_en, r'  \item ']
    
    # ==== 找到所有列表 ====
    while not ("==document body ends" in tex_file[line_idx] or r"\end{document}" in tex_file[line_idx]):
        line=tex_file[line_idx]
        if ("== DO NOT TRANSLATE" in line):
            pass
        if re.search(r'\\begin\{(?:itemize|enumerate)\}',line) and not ("== DO NOT TRANSLATE" in line):
            list_start_idx=line_idx
            list_end_idx=FindFirst(r'\\end\{(?:itemize|enumerate)\}',tex_file[list_start_idx:])+list_start_idx

            a_list_en=tex_file[list_start_idx:list_end_idx+1].copy()
            data_list.append([list_start_idx,list_end_idx,a_list_en])
            
            # a_list_zh=a_list_en.copy()
            flag=0

            for list_idx,list_line in enumerate(a_list_en):
                searchobj=re.search(r'\\item (.*)',list_line) # 找个item
                if searchobj: # 确保item行格式正确
                    text_en=searchobj.group(1)
                    data_listline.append([list_start_idx, list_idx, text_en, r'  \item '])
                    # client, text_zh = translate_text(client, text_en)
                    # a_list_zh[list_idx]=r'  \item '+text_zh+'\n' 
                else: # 其它行就随缘吧
                    flag+=len(re.findall(r'\\begin{.*}',line))  #子环境层数
                    if not flag:
                        text_en=list_line
                        data_listline.append([list_start_idx, list_idx, text_en, r''])
                        # client, text_zh = translate_text(client, text_en)
                        # a_list_zh[list_idx]=text_zh+'\n'
                    flag-=len(re.findall(r'\\end{.*}',line))


            together=['\\enzhbox{\n',] + a_list_en + ['\n}{\n',] + a_list_en + ['\n}\n',]
            # tex_file=tex_file[:list_start_idx] + together + tex_file[list_end_idx+1:]
            line_idx=list_start_idx+len(together)+1
            count+=1
            if not (client.translator_name == "count_char_num"):
                ProgressBar(count,total_num)
            # print(f'\r已翻译了 {count}/{total_num} 个itemize/enumerate环境……',end='')
            sys.stdout.flush()
            sleep(0.001)
        else:
            line_idx+=1
    
    # ==== 翻译所有文本 ====
    NN=len(data_listline)
    if client.translator_name == "doubao_async":
        ProgressBar_par(NN)
        # 控制同时进行的异步任务的数量，原理不明
        sema = asyncio.Semaphore(100) 
        
        tasks = [  asyncio.create_task( taowa(client,item[2],sema) )  for item in data_listline  ]
        zhdata = await asyncio.gather(*tasks) 
    else:
        # tasks = [  client.trans_text(item[1])  for item in data  ]
        # zhdata = list(tasks)
        zhdata=[]
        for i in range(NN):
            client, line_zh = translate_text(client, data_listline[i][2])
            zhdata.append(line_zh)
            ProgressBar(i,NN)
    
    
    # ==== 组装回列表 ====
    bias=0
    for thislist in data_list:
        list_start_idx = thislist[0]
        list_end_idx   = thislist[1]
        list_en        = thislist[2]
        
        idx4thislist = [ i for i,item in enumerate(data_listline) if item[0]==list_start_idx ]  # 挑出data_listline中属于thislist的lines
        listidx4thislist =[ data_listline[j][1] for j in idx4thislist ]  # thislist中的行号
        linezh4thislist = [ zhdata[j]           for j in idx4thislist ]  # 对应行号的译文
        linepfx4thislist =[ data_listline[j][3] for j in idx4thislist ]  # 前缀（「\item」或者空）
        
        list_zh=list_en.copy()
        for k,list_idx in enumerate(listidx4thislist):
            list_zh[list_idx] = linepfx4thislist[k] + linezh4thislist[k] + "\n"  # 对应行号的文本改成译文

        together=['\\enzhbox{\n',] + list_en + ['\n}{\n',] + list_zh + ['\n}\n',]
        tex_file=tex_file[: list_start_idx+bias ] + together + tex_file[ list_end_idx+bias+1 :]
        
        bias = len(together)-(list_end_idx-list_start_idx+1)
        
    
    
    return tex_file
    

def translate_list(client, tex_file):
    # 用来翻译itemize和enumerate环境中的文本
    print('[**] 翻译itemize和enumerate环境……')
    # client=tt.create_client()
    # def doit(mo): # 图注翻译替换函数
    #     text_en=mo.group(1)
    #     client, text_ch=translate_text(client,text_en)
    #     text_ch="\\caption{\\uline{"+text_en+ "}\\\\" + text_ch + "}"
    #     return text_ch

    start_idx=FindFirst("==document boby begins",tex_file)
    if not start_idx:
        start_idx=FindFirst(r"\\begin{document}",tex_file)
    # end_idx=FindFirst("==document body ends",tex_file)
    # if not end_idx:
    #     end_idx=FindFirst(r"\\end{document}",tex_file)

    line_idx=start_idx
    count=0
    total_num=len(re.findall(r'\\begin\{(?:itemize|enumerate)\}',' '.join(tex_file)))
    if total_num==0:
        print("未找到，",end="")
        
    while not ("==document body ends" in tex_file[line_idx] or r"\end{document}" in tex_file[line_idx]):
        line=tex_file[line_idx]
        if ("== DO NOT TRANSLATE" in line):
            pass
        if re.search(r'\\begin\{(?:itemize|enumerate)\}',line) and not ("== DO NOT TRANSLATE" in line):
            list_start_idx=line_idx
            list_end_idx=FindFirst(r'\\end\{(?:itemize|enumerate)\}',tex_file[list_start_idx:])+list_start_idx

            a_list_en=tex_file[list_start_idx:list_end_idx+1].copy()
            a_list_zh=a_list_en.copy()
            flag=0

            for list_idx,list_line in enumerate(a_list_en):
                searchobj=re.search(r'\\item (.*)',list_line) # 找个item
                if searchobj: # 确保item行格式正确
                    text_en=searchobj.group(1)
                    client, text_zh = translate_text(client, text_en)
                    a_list_zh[list_idx]=r'  \item '+text_zh+'\n' 
                else: # 其它行就随缘吧
                    flag+=len(re.findall(r'\\begin{.*}',line))  #子环境层数
                    if not flag:
                        text_en=list_line
                        client, text_zh = translate_text(client, text_en)
                        a_list_zh[list_idx]=text_zh+'\n'
                    flag-=len(re.findall(r'\\end{.*}',line))


            together=['\\enzhbox{\n',] + a_list_en + ['\n}{\n',] + a_list_zh + ['\n}\n',]
            tex_file=tex_file[:list_start_idx] + together + tex_file[list_end_idx+1:]
            line_idx=list_start_idx+len(together)+1
            count+=1
            if not (client.translator_name == "count_char_num"):
                ProgressBar(count,total_num)
            # print(f'\r已翻译了 {count}/{total_num} 个itemize/enumerate环境……',end='')
            sys.stdout.flush()
            sleep(0.001)
        else:
            line_idx+=1
    
    print("已完成。")
    return tex_file


def AIsummary(client,tex,format_AIsum:str):
    print("[**] AI总结中……",end="")
    rsp :str =client.asksth("总结上面翻译的论文的内容")
    
    # 提行加粗换为latex格式
    rsp=rsp.replace("\n","\n\n")
    rsp=re.sub(r"\*\*(.*?)\*\*",r"\\textbf{\1}",rsp)
    rsp=re.sub(r"^[ \t]*-",r"  •",rsp)
    
    # 装进去
    insert_id=FindFirst(r"%  == insert here",format_AIsum)
    format_AIsum[insert_id]=rsp+"\n"
    start_idx=FindFirst("==document boby begins",tex)
    tex=tex[:start_idx-1]+format_AIsum+tex[start_idx:]
    print("已完成")
    return tex
    


    

def post_decoration(tex):
    begin=FindFirst("==document boby begins",tex)
    if not begin: begin=0
    end=FindFirst("==document boby ends",tex)
    if not end : end=len(tex)
    for idx in range(begin,end):
        line=tex[idx]
        line=post_decoration_line(line)
        tex[idx]=line
    return tex

def post_decoration_line(line):
        line=re.sub(r"([图表] ?\d+\.?(?:\d+)?)",r"\\textcolor{blue}{\1}",line)
        line=re.sub(r"([\(（]\d+[\.-]\d+[a-g]?[\)）])",r"\\textcolor{violet}{\1}",line)
        line=re.sub(r"(\[(?:\d+[,-]? ?)+\])",r"\\textcolor{green!50!black}{\1}",line)
        line=re.sub(r'"(.*?)"',r"「\1」",line)
        line=re.sub(r'“(.*?)”',r"「\1」",line)
        line=line.replace(r'\\%',r'\%')
        # line=re.sub(r"%",r"\%",line)
        return line


if __name__=="__main__":
    # 测试
    # lines=[
    #     r"Right-hand side: Current profiles for discharge 119787 of DIIID: total $\left(J_{\|}\right)$, bootstrap $\left(J_{\text {bs }}\right)$, beam driven $\left(J_{\mathrm{NBCD}}\right)$ current densities, and the sum of the bootstrap and beam-driven current densities. After (ref.[55]).",
    
    #     #r"\command{233} Because of the divergence-free nature of the magnetic field, the simplest topological configuration it can assume with no field lines exiting from a fixed volume is toroidal.",
    #     #r"Introduce general 95\% coordinates $\psi, \theta, \zeta$, as shown in Fig. 1.2. Surfaces of constant $\psi$ are taken to consist topologically of nested tori, which necessarily possess an axis which will usually be designated by $\psi=0$."
    #     ]
    
    from importlib import import_module
    
    translatorsdict={"1":"baidu","2":"tencent","3":"openai","4":"deepl","5":"doubao","9":"test","0":"count_char_num"}
    s=input("<< 选择翻译器"+str(translatorsdict)+"：")

    # exec("import translators."+translatorsdict[s]+"_translator as tt ") # 感觉不太优雅，但是就这样吧！
    tt=import_module("translators."+translatorsdict[s]+"_translator")

    client=tt.create_client()
    # for line in lines:
    # print(line)
    while(1):
        line=input("input en:")
        head =r'\noindent ' if re.search(r'^[a-z]',line) else ''
        # print(head)
        client, line_ch=translate_text(client,line)
        output="\n"+r"\enzhbox{  "+head+line+"}{\n"+head+line_ch+"}\n"
        output=post_decoration_line(output)
        print(output)


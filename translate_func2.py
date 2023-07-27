"""
翻译器在translators文件夹中，通过修改下面import哪个文件来决定用那个翻译库。
这些翻译库都需要自备api。
支持的服务商：
openai（chatGPT3.5），deepl，baidu，tencent
"""

translatorsdict={"1":"baidu","2":"tencent","3":"openai","4":"deepl","5":"test"}
s=input("<< 选择翻译器"+str(translatorsdict)+"：")

# tt=__import__(translatorsdict[s]+"_translator")
exec("import translators."+translatorsdict[s]+"_translator as tt ") # 感觉不太优雅，但是就这样吧！
# from baidu_translator import * 


import re,sys
from time import sleep

def FindFirst(pat,lst,flg=0):  #找到字符串数组lst中第一次正则匹配到pat的索引位置
    try:
        i=lst.index(next(filter(re.compile(pat,flags=flg).search,lst)))
    except StopIteration: # 一个也没找到
        i=None
    return i

def ProgressBar(now,alls):
    progress=int(now/alls*50)
    print("\r进度: %d/%d: "%(now,alls), "▋"*progress + "-"*(50-progress), end="")
    if now==alls:
        print("done！")   #100%了换个行
    sys.stdout.flush()
    sleep(0.01)

def translate_text(client,text):
    
    inline_eqn_results = re.findall(r'\$.*?\$|\\\w+(?:{.*?})?|\\%',text) # 预处理行内公式
    # print(inline_eqn_results)
    
    for i in range(len(inline_eqn_results)):
        inline_eqn=inline_eqn_results[i]
        marker='xx'+'%02d'%i  # 把行内公式替换成标记，防止翻译时丢符号
        text = text.replace(inline_eqn,marker)
    
    text = re.sub(r'(Chaps?\.|Secs?\.|Eqn?s?\.|Refs?\.|Figs?\.) (\(?\d+\)?)',r'\1\2',text,flags=re.IGNORECASE)  # 把诸如「Sec. 3」变成「Sec.3」，防止这个点被认成句号导致错误断句。

    text_zh=tt.translator(client,text)
    
    for i in range(len(inline_eqn_results)):
        inline_eqn=inline_eqn_results[i]
        marker='xx'+'%02d'%i
        text_zh = text_zh.replace(marker,inline_eqn) # 替换回来

    return text_zh


def translate_abstract(tex_file):
    st = r'\\begin{abstract}'
    st1 = r'\\title\{(.*?)\}'
    print('Translating abstract')

    client=tt.create_client()

    title_idx=FindFirst(st1,tex_file)
    if title_idx:
        title_en=re.search(st1,tex_file[title_idx]).group(1)
        title_zh=translate_text(client,title_en)
        tex_file[title_idx]=r'\title{'+title_zh+r'\\ \Large{'+title_en+'}}'
        print("标题：",title_zh)
    else:
        print("no title found!")

    abstract_idx=FindFirst(st,tex_file)
    if abstract_idx:
        abstract_idx+=1
        abstract_en = tex_file[abstract_idx]
        abstract_ch = translate_text(client,abstract_en)+'\n'
        tex_file[abstract_idx] = r'\uline{'+abstract_en+r'}\\ \indent '+abstract_ch
    else:
        print("no abstract found!")
    
    return tex_file

def translate_body(tex_file,suffix):
    # sub_environ=r'\\(begin|end)\{.*\}'
    # sub_title=

    # st0 = r'\maketitle'
    # st1 = r'\section'
    # st2 = r'{References}'
    # sx1 = r'{figure}'
    # sx2 = r'{equation}'
    # sx3 = r'{table}'
    
    print('Translating main body')

    client=tt.create_client()
    def doit(mo): # 图注翻译替换函数
        text_en=mo.group(1)
        text_ch=translate_text(client,text_en)
        text_ch="\\caption{\\uline{"+text_en+ "}\\\\" + text_ch + "}"
        return text_ch

    start_idx=FindFirst("==document boby begins",tex_file)
    end_idx=FindFirst("==document body ends",tex_file)
    
    flag = 0
    L = end_idx-start_idx+1
    for line_idx in range(start_idx,end_idx):
        line = tex_file[line_idx]
        ProgressBar(line_idx-start_idx+1,L-1)
        # print(line_idx-start_idx+1,'/',L)

        flag+=len(re.findall(r'\\begin{.*}',line))  #子环境层数

        if flag==0 and len(line)>2: # 非子环境内
            searchobj=re.search(r'\\(chapter|section|subsection)\{(.*?)\}',line) # 搜寻章节标题
            if searchobj: # 章节标题的处理
                name_en=searchobj.group(2)
                name_ch=translate_text(client, name_en.lower())
                line_ch=line.replace(name_en,name_ch)+'\n {  \\small '+name_en+'\\par }\n'
                tex_file[line_idx] = line_ch
            else: # 普通正文的处理
                line_ch = translate_text(client, line)+'\n'
                # tex_file[line_idx] = r"\begin{leftbar} \small "+line+r"\end{leftbar}"+line_ch # 翻译后，在前面放上原文
                # tex_file[line_idx] = "\n"+r"\begin{supertabu} to 1\linewidth [t]{|X[l]|X[l]} \small "+line+r"&"+line_ch+r"\end{tabu} \medskip" # 翻译后，在前面放上原文
                tex_file[line_idx] = "\n"+r"\enzhbox{  "+line+"}{\n"+line_ch+"}\n"

        if not flag==0: # 子环境内
            tex_file[line_idx]=re.sub(r'\\caption{(.*)}',doit,line) # 翻译图注
        
        flag-=len(re.findall(r'\\end{.*}',line))

    tex_file[end_idx+1]=suffix # 接回尾巴
    return tex_file

def translate_captions(tex_file):
    print('Translating captions')
    client=tt.create_client()
    def doit(mo):
        text_en=mo.group(1)
        text_ch=translate_text(client,text_en)
        text_ch="\\caption{"+text_en+ "\\\\" + text_ch + "}"
        return text_ch
    
    L=len(tex_file)
    for line_idx, line in enumerate(tex_file):
        ProgressBar(line_idx+1,L)
        tex_file[line_idx]=re.sub(r'\\caption{(.*)}',doit,line)

    return tex_file

def post_decoration(tex):
    for idx,line in enumerate(tex):
        tex[idx]=re.sub(r"(图 ?\d+\.?(?:\d+)?)",r"\\textcolor{blue}{\1}",line)

    return tex

if __name__=="__main__":
    # 测试
    lines=[r"\command{233} Because of the divergence-free nature of the magnetic field, the simplest topological configuration it can assume with no field lines exiting from a fixed volume is toroidal.",
        r"Introduce general 95\% coordinates $\psi, \theta, \zeta$, as shown in Fig. 1.2. Surfaces of constant $\psi$ are taken to consist topologically of nested tori, which necessarily possess an axis which will usually be designated by $\psi=0$."]
    client=tt.create_client()
    for line in lines:
        print(line)
        line_zh=translate_text(client,line)
        print(line_zh)


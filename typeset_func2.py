import re,requests,logging
from typing import List, Union

def FindFirst(pat : str,lst : list,flg=0):  #找到字符串数组lst中第一次正则匹配到pat的索引位置
    try:
        i=lst.index(next(filter(re.compile(pat,flags=flg).search,lst)))
    except StopIteration: # 一个也没找到
        i=None
    return  i

def myfind(lst):
    idxlst=[]
    for i,thing in enumerate(lst):
        if thing:
            idxlst.append(i)
    
    return idxlst


#在tex_file中找到st,并在st的{}中插入content
def insert_tex(tex_file,st,content):
    pattern=st+r'(.*){}(.*)'
    replace=st+r'\1{'+repr(content)[1:-1]+r'}\2' # repr()一下，否则转义失效的话会出错
    for idx,line in enumerate(tex_file):
        if st in line:
            tex_file[idx]=re.sub(pattern,replace,line)  
    # for line_idx, line in enumerate(tex_file):
    #     if st in line:
    #         insert_line = line
    #         insert_idx = line_idx
    #         break
    # for c_idx,c in enumerate(insert_line):
    #     if c=='{':
    #         k_idx = c_idx+1
    #         break
    # new_line = insert_line[:k_idx]+content+insert_line[k_idx:]
    # tex_file[insert_idx] = new_line
    return tex_file

def get_format_figure(tex_template):
    head_idx=FindFirst(r'==figure format begins',tex_template)
    tail_idx=FindFirst(r'==figure format ends',tex_template)
    return tex_template[head_idx+1:tail_idx]

def get_format_equation(tex_template):
    head_idx=FindFirst(r'==equation format begins',tex_template)
    tail_idx=FindFirst(r'==equation format ends',tex_template)
    return tex_template[head_idx+1:tail_idx]

def get_format_table(tex_template):
    head_idx=FindFirst(r'==table format begins',tex_template)
    tail_idx=FindFirst(r'==table format ends',tex_template)
    return tex_template[head_idx+1:tail_idx]

def get_format_AIsummary(tex_template):
    head_idx=FindFirst(r'== AIsummary format begins',tex_template)
    tail_idx=FindFirst(r'== AIsummary format ends',tex_template)
    return tex_template[head_idx+1:tail_idx]


def create_new_tex(tex_template):
    end_idx=FindFirst(r'\\end{document}',tex_template)
    return tex_template[0:end_idx+1]

def getpaperref(thetitle :str) -> str:
    # 使用semantic scholar的api来获取当前文章的引用
    # 2025-03-07 15-15-05
    print("查询该文章的引用……",end="")
    try:
        # 以标题查询该文章
        response = requests.get(
                    "http://api.semanticscholar.org/graph/v1/paper/search/bulk", 
                    params={"query": f'"{thetitle}"'})
        r= response.json()['data'][0]
        gettitle :str= r['title']
        gettitle=re.sub(r"[^\u0000-\u00ff]","",gettitle)
        # 查询到的文章标题应该与输入的文章标题一样
        assert thetitle.lower().strip() == gettitle.lower().strip(), f"Expected title: {thetitle}, but got: {r['title']}"

        # print(r)
        # print(r['paperId']) # 这篇文章的id

        # 以id查询这篇文章的详细信息
        paper = requests.post(
                'https://api.semanticscholar.org/graph/v1/paper/batch',
                params={'fields': 'title,journal,year,authors.name,externalIds'},
                json={"ids": [r['paperId']]}
        )
        p=paper.json()[0]
        # print(p)
        # print(p["title"])
        # print(p["year"])
        # print(p["journal"]["name"])
        # print([ au["name"] for au in p["authors"]])

        # 形如：张三 (2021). 某某期刊. doi: 10.123456
        totex=f'{p["authors"][0]["name"]} ({p["year"]}). {p["journal"]["name"]}. doi: \\href{{https://www.doi.org/{p["externalIds"]["DOI"]}}}{{{p["externalIds"]["DOI"]}}}'
        todisp=f'{p["authors"][0]["name"]} ({p["year"]}). {p["journal"]["name"]}. doi: {p["externalIds"]["DOI"]}'
        print(todisp)
        logging.warning("在semantic scholar找到该文章信息："+todisp)
    except:
        todisp=""
        totex=""
        print("未找到引用")
        logging.warning("在semantic scholar未找到该文章信息")
    
    return totex
    

def modify_title(tex_0,tex_1):
    title=''
    title_idx=FindFirst(r'\\title\{.*?',tex_0) 
    if title_idx:
        if r'}' in tex_0[title_idx]: # 标题只有一行
            title=re.search(r'\\title\{(.*?)\}',tex_0[title_idx]).group(1)
        else: # 多行
            title_idx_end=title_idx+1+FindFirst(r'\}',tex_0[title_idx+1:])
            title_raw=' '.join(tex_0[title_idx:title_idx_end+1]).replace('\n','')
            title=re.search(r'\\title\{(.*?)\}',title_raw).group(1)

        print('标题:',title)
    
    title_idx1=FindFirst(r'\\title{(.*)}',tex_1)
    if title_idx1:
        tex_1[title_idx1]=r'\title{'+title+'}\n'   # 若模板里有标题栏，则插入

    
    paperref=getpaperref(title.replace("$","").replace(r"\\","").replace(r"\textit{","").replace(r"\textbf{","").replace("}","").strip())
    if paperref:
        paperref_idx=FindFirst(r'== paperref here ==',tex_1)
        tex_1[paperref_idx]=tex_1[paperref_idx].replace('== paperref here ==',paperref)
    
    return tex_1
    

def modify_author(tex_0,tex_1):
    author=""
    author_idx=FindFirst(r'\\author{',tex_0)
    if author_idx: # 如有作者
        aths_raw=re.search(r'\\author\{(.*)\}?',tex_0[author_idx]).group(1).replace("}","")
        aths_raw=re.sub(r'\$.*?\$','',aths_raw) # 删去可能的角标
        aths=aths_raw.split(',')
        for i,ath in enumerate(aths):
            author=author+ath
            if i<2: # 最多三个作者
                author=author+', '
            else: # 后面的省略
                author=author+" et al."
                break
        author=author.replace('\n','').replace(r'\\','')
        # print("作者："+author)
        print("")
    
    author_idx1=FindFirst(r'\\author{(.*)}',tex_1)
    if author_idx1:
        tex_1[author_idx1]=r'\author{'+author+'}\n' # 若模板里有作者栏，则插入

    return tex_1


def modify_abstract(tex_0,tex_1):
    abstract=""
    abstract_idx=FindFirst(r'\\begin{abstract}',tex_0)
    insert_idx=FindFirst(r'==abstract here',tex_1)
    
    if abstract_idx and insert_idx: # 如有摘要，则插入
        abstract = tex_0[abstract_idx+1]
        tex_1[insert_idx]=abstract
    return tex_1


def modify_body(tex_0,tex_1):

    start_idx=FindFirst(r'\\end{abstract}',tex_0) # 寻找正文开始处
    if not start_idx:
        start_idx=FindFirst(r'\\begin{document}',tex_0) # 保底

    end_idx=0#FindFirst(r'{references?}|{acknowledgments?}',tex_0,flg=re.I) # 寻找正文结束处
    if not end_idx:
        end_idx=FindFirst(r'\\end{document}',tex_0) # 保底

    body = tex_0[start_idx+1:end_idx-1]
    

    insert_idx=FindFirst(r'==document body here',tex_1) # 在新文档中插入正文
 
    tex_1_new=tex_1[:insert_idx]+body+tex_1[insert_idx+1:]

    return tex_1_new


def modify_pre(tex):
    # 预处理，2025-03-10 11-58-44
    
    # 处理该死的脚注
    idx=FindFirst(r"==document boby begins",tex)
    while idx<len(tex)-1:
        if r"\footnotetext" in tex[idx]:  # 找到该死的脚注
            jdx=idx
            flag=len(re.findall(r"\{",tex[jdx]))-len(re.findall(r"\}",tex[jdx]))
            while flag>0:
                jdx += 1
                flag += len(re.findall(r"\{",tex[jdx]))-len(re.findall(r"\}",tex[jdx]))
            tex[jdx]=re.sub(r"^ *\}"," }\n",tex[jdx])
            afootnote=' '.join([l.strip() for l in tex[idx:jdx+1]])+"\n" # 拼接脚注为一行
            afootnote=re.sub(r"(.*\})","\\1\n",afootnote)
            
            tex[idx]=afootnote
            tex[idx+1:jdx+1]=['% ==AUTO MOVED1 \n']*len(tex[idx+1:jdx+1])
            idx=jdx+1
        else:
            idx += 1
            
    return tex
    

def get_suffix(tex_0): # 把参考文献那些摘除，等翻译完再接回来
    suffix=""
    ref_idx=FindFirst(r'\\\w*section\*?({references?}|{acknowledgments?})',tex_0,flg=re.I)
    end_idx=FindFirst(r'==document body ends',tex_0)
    
    if not ref_idx: # 再挣扎一下
        idx= end_idx
        ref_ali=0
        while idx>end_idx-10:
            if re.search(r'\[\d+\]|\^\{\d+\}',tex_0[idx]) \
            and re.search(r'\[\d+\]|\^\{\d+\}',tex_0[idx-1]) \
            and  re.search(r'\[\d+\]|\^\{\d+\}',tex_0[idx-2]):  # 三行连续的参考文献标记
                ref_ali=1
                break
            idx-=1
        if ref_ali:
            while idx>end_idx-100:
                if re.search(r'\[1\]|\^\{1\}',tex_0[idx]):
                    break
                idx-=1
            ref_idx=idx
            
            
    
    if ref_idx :
        suffix=''.join(tex_0[ref_idx:end_idx-1])
        tex_01=tex_0[:ref_idx-1]+tex_0[end_idx:]
    else:
        suffix=""
        tex_01=tex_0
        
    return tex_01, suffix

def modify_equation1(tex,format_equation):
    # 202405之前的某个时间，mathpix可以保留公式编号了，所以不需要做额外的处理了
    flag=0
    for [i,line] in enumerate(tex):
        tex[i]=tex[i].replace(r"{equation*}",r"{align*}")
        tex[i]=re.sub(r"^ *\\\[", r"\\begin{align*}",tex[i])
        tex[i]=re.sub(r"^ *\\\]", r"\\end{align*}",tex[i])
        
        if r'$$' in line :
            if flag==0 :
                tex[i]=line.replace(r"$$",r"\begin{align*}")
                flag=1
            else:
                tex[i]=line.replace(r"$$",r"\end{align*}")
                flag=0

    return tex
        

def modify_equation(tex,format_equation):
    idx=0
    while idx<len(tex):
        line=tex[idx]
        if re.match(r'\$\$',line):#'$$' in line:
            start_idx=idx
            end_idx=FindFirst(r'\$\$',tex[start_idx+1:])+start_idx+1

            # 把公式内容内容提取出来，插入模板的公式环境中
            eqn_body=tex[start_idx+1:end_idx]

            # 读取模板
            fmt_eqn=format_equation.copy()
            



            # 以下内容仅在模板为align时启用
            if 'align' in fmt_eqn[0]:
                if re.search(r'\\begin\{.*ed\}',eqn_body[0]):  # 删除aligned或gathered环境
                    del eqn_body[0]
                if re.search(r'\\end\{.*ed\}',eqn_body[-1]):
                    del eqn_body[-1]

                
                splited = False # 是否有断行公式
                equals=r'(?:=|\\sim|\\equiv|\\approx|\\simeq|\\neq|\\propto)'  # 各种「等于」符号
                calcs=r'(?:\+|-|\\times|\\cdot|\\pm)' # 各种象征断行的计算符号

                # 初步处理
                flag = 0 # 子环境层数
                flag_boss =0
                for idx in range(0,len(eqn_body)):  
                    eqnline=eqn_body[idx].strip()
                    

                    if r'\begin{array}' in eqnline:
                        flag += 1
                        if re.search(r'^ ?\\begin\{array\}(?:\{.*\})?',eqnline):
                            flag_boss +=1
                            eqnline=re.sub(r'^ ?\\begin\{array\}(?:\{.*\})?',r'\\begin{aligned}',eqnline)
                        
                    if r'\end{array}' in eqnline:
                        if flag == flag_boss:
                            eqnline=eqnline.replace(r'\end{array}',r'\end{aligned}')
                            flag_boss=-1
                        flag -= 1

                    if flag==0: # 若不在array环境中
                        if len(re.findall('&',eqnline))<=1: # 如果只有一个&
                            eqnline=eqnline.replace('&','').strip() # 删去原本的&
                        
                        
                        
                    # eqnline=re.sub(r'^ ?\\begin\{array\}(?:\{.*\})?',r'\\\1{aligned}',eqnline)
                    eqn_body[idx]=eqnline+'\n'

                flag=0
                # 划分aligned块
                # 两种划分模式：
                # 1. 断行：一行有equals符号且不在句首的，其后接了数行没有equals符号的
                # 2. 推导：一行没有equals符号或equals符号不在句首的，接了数行equals符号位于句首的

                def add_aligned_block(eqn_body,idx_begin,idx_end):
                    eqn_body[idx_begin] = r'& \begin{aligned}'+' \n'+eqn_body[idx_begin]
                    if r'\\' in eqn_body[idx_end]: # idx_end是否是最后一行
                        eqn_body[idx_end] = eqn_body[idx_end].replace(r'\\','\n'+r'\end{aligned} \\')
                    else:
                        eqn_body[idx_end] = eqn_body[idx_end].strip()+'\n'+r'\end{aligned}'+'\n '
                    return eqn_body

                def replace_first_real_one(pat,rep,eqnline):
                    to_reserve=[r'\{.*?\}',    # 为了做到括号里面的不替换，真是大费周章……      
                                r'\[.*?\]', 
                                r'\(.*?\)',             
                                ]
                    reserved = re.findall('|'.join(to_reserve),eqnline) 
                    for i in range(len(reserved)):
                        inline_eqn=reserved[i]
                        marker='xx'+'%02d'%i  # 把行内公式替换成标记，防止翻译时丢符号
                        eqnline = eqnline.replace(inline_eqn,marker)
                    if re.search(pat,eqnline):
                        eqnline = re.sub(pat,rep,eqnline,count=1)
                    else:
                        eqnline = re.sub('^()',rep,eqnline,count=1)
                    for i in range(len(reserved)):
                        inline_eqn=reserved[i]
                        marker='xx'+'%02d'%i
                        eqnline = eqnline.replace(marker,inline_eqn) # 替换回来
                    return eqnline

                idx=0
                flag = 0 # 子环境层数
                while(idx<len(eqn_body)):
                    eqnline=eqn_body[idx].strip()
                    flag+=len(re.findall(r'\\begin{.*}',eqnline))
                    if flag: # 身处子环境中，什么都不做
                        flag-=len(re.findall(r'\\end{.*}',eqnline))
                        idx += 1
                        continue

                    if '&' in eqnline: # 原本有对齐符号，什么也不做
                        idx += 1
                        continue

                    idx_begin=idx

                    if idx == len(eqn_body)-1:
                        eqn_body[idx] = r'& ' + eqn_body[idx]
                        break
   
                    
                    # 推导
                    # 第一行没有等号或等号不在句首，第二行的句首是等号或运算符，且第二行没有不在句首的等号
                    elif ((not re.search(equals,eqnline)) or re.search(r'(?!^)'+equals,eqnline))  \
                     and (re.search(r'^(\\left.)?('+equals+'|'+calcs+')',eqn_body[idx+1]) \
                     and (not re.search(r'(\\left.)?(?!^)'+equals,eqn_body[idx+1]) ) ):
                        for idx1 in range(idx_begin+1,len(eqn_body)): # 搜索其后有多少行有位于句首的等号
                            if (not re.search(r'^(\\left.|\\quad)*('+equals+'|'+calcs+')',eqn_body[idx1])): # 找到一行句首不是等号或运算符的，则止步与上一行
                                idx_end = idx1-1
                                break
                            if idx1==(len(eqn_body)-1): # 直到最后一行都有位于句首的等号，则止步于最后一行
                                idx_end = idx1
                        if idx_begin != idx_end: # 存在推导的块
                            if re.search(equals,eqn_body[idx_begin]):
                                eqn_body[idx_begin] = replace_first_real_one(r'('+equals+r')',r'& \1',eqn_body[idx_begin])
                            else:
                                eqn_body[idx_begin] = r'& ' + eqn_body[idx_begin]
                            for idx1 in range(idx_begin+1,idx_end+1):
                                if re.search(equals,eqn_body[idx1]):
                                    eqn_body[idx1] = r'& ' + eqn_body[idx1]
                                else:
                                    eqn_body[idx1] = r'& \qquad ' + eqn_body[idx1]

                            eqn_body = add_aligned_block(eqn_body,idx_begin,idx_end)
                            idx=idx_end+1 # 移动到块的后面
                        else:
                            eqn_body[idx] = r'& ' + eqn_body[idx]
                            idx += 1

                    # 断行
                    # 有不在句首的等号，且下一行是运算符开头
                    # elif re.search(r'(?!^)'+equals,eqnline) and re.search(r'^(\\left.)?('+calcs+')',eqn_body[idx+1]): 
                    #     for idx1 in range(idx_begin+1,len(eqn_body)): # 搜索其后有多少行没有等号
                    #         if not re.search(r'^(\\left.|\\quad)*'+calcs,eqn_body[idx1]): # 找到一行不是计算符号开头的的，则止步与上一行
                    #             idx_end = idx1-1
                    #             break
                    #         if idx1==(len(eqn_body)-1): # 直到最后一行都没有等号，则止步于最后一行
                    #             idx_end = idx1
                    #     if idx_begin != idx_end: # 存在断行的块
                    #         eqn_body[idx_begin] = replace_first_real_one(r'('+equals+r')',r'& \1',eqn_body[idx_begin])
                    #         for idx1 in range(idx_begin+1,idx_end+1):
                    #             eqn_body[idx1] = r'& \qquad ' + eqn_body[idx1]
                    #         eqn_body = add_aligned_block(eqn_body,idx_begin,idx_end)
                    #         idx=idx_end+1 # 移动到块的后面
                    #     else:
                    #         eqn_body[idx] = r'& ' + eqn_body[idx]
                    #         idx += 1

                    else:
                        eqn_body[idx] = r'& ' + eqn_body[idx]
                        idx +=1

            
            # 为什么不用管第二个$$：因为end_idx已经找到了第二个$$，通过tex[end_idx+1:]已经把它排除了      
            # 
            
            insert_idx=FindFirst("==here",fmt_eqn)
            fmt_eqn=fmt_eqn[:insert_idx]+eqn_body+fmt_eqn[insert_idx+1:]   
            tex=tex[:start_idx]+fmt_eqn+tex[end_idx+1:]     
        idx+=1
    
    return tex
    
# def modify_equation(tex,format_equation):
#     idx=0
#     while idx<len(tex):
#         line=tex[idx]
#         if '$$' in line:
#             start_idx=idx
#             end_idx=FindFirst(r'\$\$',tex[start_idx+1:])+start_idx+1

#             # 把公式内容内容提取出来，插入模板的公式环境中
#             fmt_eqn=format_equation.copy()
#             insert_idx=FindFirst("==here",fmt_eqn)
#             fmt_eqn=fmt_eqn[:insert_idx]+tex[start_idx+1:end_idx]+fmt_eqn[insert_idx+1:]



#             # 以下内容仅在模板为align时启用
#             if 'align' in fmt_eqn[0]:
#                 if re.search(r'\\begin\{.*ed\}',fmt_eqn[1]):  # 删除aligned或gathered环境
#                     del fmt_eqn[1]
#                 if re.search(r'\\end\{.*ed\}',fmt_eqn[-2]):
#                     del fmt_eqn[-2]

#                 flag = 0 # 子环境层数
#                 splited = False # 是否有断行公式
#                 equals=r'=|\\sim|\\equiv|\\approx|\\simeq|\\neq'  # 各种「等于」符号

#                 # 初步处理
#                 for idx in range(1,len(fmt_eqn)-1):  # 设置对齐
#                     eqnline=fmt_eqn[idx].strip()

#                     # if re.search(r'^ ?\\(begin|end)\{array\}(?:\{.*\})?',eqnline):
#                     eqnline=re.sub(r'^ ?\\(begin|end)\{array\}(?:\{.*\})?',r'\\\1{aligned}',eqnline)

#                     flag+=len(re.findall(r'\\begin{.*}',eqnline))  
#                     if (flag==0): # 不在子环境中，则添加&
#                         eqnline=eqnline.replace('&','').strip() # 删去原本的&

#                         # 添加&
#                         if '=' in eqnline:
#                             eqnline=r'& '+eqnline   # 左对齐
#                             # eqnline=eqnline.replace('=','&=') # 等号处对齐
#                         else : # 该行没有等号，大概是上行的分段
#                             eqnline=r'&\qquad '+eqnline


#                         # 划分aligned块

#                         # 两种划分模式：
#                         # 1. 断行：一行有equals符号的，其后接了数行没有equals符号的
#                         # 2. 推导：一行没有equals符号或equals符号不在句首的，接了数行equals符号位于句首的

#                         # if re.search(equals,eqnline): 



#                         if '=' in eqnline: # 当前行有等号 
#                             if idx<len(fmt_eqn)-1 and fmt_eqn[idx+1].strip()[0]=='=': # 下一行等号在式子最开头，说明是本行的推导
#                                 eqnline = r'\qquad '+eqnline
#                             elif ( (not r'\\' in eqnline)  or ('=' in fmt_eqn[idx+1])):# 是最后一行或下一行也有等号，则说明当前公式没有跨行
#                                 pass 
#                             else:
#                                 splited = True 
#                                 # fmt_eqn[0] = fmt_eqn[0].replace('\n','  % ==AUTO SPLITTED\n')
#                                 eqnline=r'& \begin{aligned} '+'\n'+eqnline   # 开始跨行
#                         elif splited: # 当前行无等号，大概是上一行的继续
#                             if   not r'\\' in eqnline : # 最后一行，则跨行到此结束
#                                 eqnline = eqnline.replace('\n',' \\end{aligned} \n')
#                                 splited = False
#                             elif ('=' in fmt_eqn[idx+1]): # 下一行也有等号，则跨行到此结束
#                                 eqnline = eqnline.replace('\\\\','\n \\end{aligned} \\\\')
#                                 splited = False
#                             else: #中间行
#                                 pass

#                     fmt_eqn[idx]=eqnline

#                     flag-=len(re.findall(r'\\end{.*}',eqnline))

#             tex=tex[:start_idx]+fmt_eqn+tex[end_idx+1:]
#             # 为什么不用管第二个$$：因为end_idx已经找到了第二个$$，通过tex[end_idx+1:]已经把它排除了              
#         idx+=1
    
#     return tex



def modify_figure(tex,format_figure):
    idx=0
    while idx<len(tex):
        fmt_fig=format_figure.copy()
        line=tex[idx]   # idx:「\includegraphics」所在的行
        mo=re.search(r'\\includegraphics\[.*\]{(.*)}',line)
        if mo:
            file=mo.group(1)    # 文件名
            idx_of_caption=0
            fmt_fig = insert_tex(fmt_fig,'includegraphics',file)
            
            idx2search=[] # 向上向下交替搜索
            for x, y in zip(range(idx+1,idx+6), range(idx-1,idx-6,-1)): idx2search.extend([x, y])
            
            for idx1 in idx2search:  # idx1：题注文本所在的行
                line1=tex[idx1]
                
                mo1=re.search(r'^(?:(?:fig|f1g)(?:ure)?|图)\.? *((?:\d+|[A-Z]|[一-鿆]|\$)\.?(?:\d+)?\.?)\:? ?(.*)',line1,flags=re.IGNORECASE)
                if mo1:
                    num=mo1.group(1) # 序号
                    cap=mo1.group(2) # 图注
                    if not re.search(r"^([A-Z]|\$|\(|[一-鿆]).*",cap): # 不是大写字母/公式/括号开头，说明不可能是题注，慎用。
                        print(f"[**]警告：图片 {file} 的图注异常，请注意检查")
                        fmt_fig.append("% == ↑↑ CHECK HERE! 图注可能异常\n")
                    tex[idx1]="" # 清空原题注行
                    fmt_fig = insert_tex(fmt_fig,'label','fig'+num)
                    fmt_fig = insert_tex(fmt_fig,'caption',cap)   
                    break
                
                # if re.search(r'fig|图',line1,flags=re.IGNORECASE):
                #     idx_of_caption=idx1
                #     mo1=re.search(r'^(?:fig(?:ure)?|图)\.? *((?:\d+|[A-Z]|[一-鿆]|\$)\.?(?:\d+)?\.?) ?(.*)',line1,flags=re.IGNORECASE)
                #     if mo1:
                #         num=mo1.group(1) # 序号
                #         cap=mo1.group(2) # 图注
                #         if not re.search(r"^([A-Z]|\$|\(|[一-鿆]).*",cap): # 不是大写字母/公式/括号开头，说明不是题注，慎用。
                #             print(f"[**]警告：图片 {file} 的图注异常，请注意检查")
                #             fmt_fig.append("% == ↑↑ CHECK HERE! 图注可能异常\n")
                #             cap=line1.strip()
                #     else:
                #         print(f"[**]警告：图片 {file} 的图注异常，请注意检查")
                #         fmt_fig.append("% == ↑↑ CHECK HERE! 图注可能异常\n")
                #         num=""
                #         cap=line1.strip()
                     
                #     tex[idx1]="" # 清空原题注行
                #     fmt_fig = insert_tex(fmt_fig,'label','fig'+num)
                #     fmt_fig = insert_tex(fmt_fig,'caption',cap)   
                #     break
            
            if r"\begin{center}" in tex[idx-1]:
                tex[idx-1]=""
            if r"\end{center}" in tex[idx+1]:
                tex[idx+1]=""



            tex=tex[:idx]+fmt_fig+tex[idx+1:]
            idx+=len(fmt_fig)
        else:
            idx+=1
    return tex


def modify_table1(tex,format_table):
    posi2insert = FindFirst("==tabular here",format_table)
    idx=0
    while idx<len(tex):
        fmt_tab=format_table.copy()
        line=tex[idx]
        if r"\begin{center}" in line:
            beginidx=idx
            endidx=FindFirst(r"\\end\{center\}",tex[idx:])+beginidx
            
            beginoftabular0=FindFirst(r"\{tabular\}",tex[beginidx:endidx])
            if isinstance(beginoftabular0,int) :
                beginoftabular=beginoftabular0+beginidx
                findsth = lambda s: r"\end{tabular}" in s
                temp = map(findsth,tex[beginoftabular:endidx])
                tempidx = myfind(temp)
                endoftabular = tempidx[-1]+beginoftabular
                tabularbody = tex[beginoftabular:endoftabular+1]
                fmt_tab=fmt_tab[:posi2insert-1]+tabularbody+fmt_tab[posi2insert+1:]
                
                idx2search=[] # 向上向下交替搜索
                for x, y in zip(range(beginoftabular-1,beginoftabular-6,-1),range(endoftabular+1,endoftabular+6)): idx2search.extend([x, y])
                
                for idx1 in idx2search: # 找表注
                    line1=tex[idx1]
                    if re.search(r'tab(?:le)?\.? ?((?:\d+|[A-Z])\.?(?:\d+)?)',line1,flags=re.IGNORECASE):
                        mo1=re.search(r'tab(?:le)?\.? ?((?:\d+|[A-Z])\.?(?:\d+)?\.?) ?(.*)',line1,flags=re.IGNORECASE)
                        num=mo1.group(1) # 序号
                        cap=mo1.group(2) # 图注
                        if not re.search(r"^([A-Z]|\$|\().*",cap): # 不是大写字母开头，说明不是题注，慎用。
                            cap=line1.strip() 
                        tex[idx1]="" # 清空原题注行
                        fmt_tab = insert_tex(fmt_tab,'label','tab'+num)
                        fmt_tab = insert_tex(fmt_tab,'caption',cap.strip())
                        break
                
                tex=tex[:beginidx]+fmt_tab+tex[endidx+1:]
                idx+=len(fmt_tab)
            else:
                idx+=1
        else:
            idx+=1
    
    return tex
            


# def modify_table(tex,format_table):
#     posi2insert=FindFirst("==tabular here",format_table)
#     idx=0
#     while idx<len(tex):
#         fmt_tab=format_table.copy()
#         line=tex[idx]
#         mo=re.search(r'\\begin\{tabular\}',line)
#         if mo:
#             tabular_begin=idx
#             tabular_end=tabular_begin+FindFirst(r'\\end\{tabular\}',tex[idx:],flg=re.IGNORECASE)
#             tabular_body=tex[tabular_begin:tabular_end+1] # 表格体
#             fmt_tab=fmt_tab[:posi2insert-1]+tabular_body+fmt_tab[posi2insert+1:]

#             for idx1 in range(idx-2,idx-10,-1): # 找表注：向上
#                 line1=tex[idx1]
#                 if re.search(r'tab(?:le)?\.? ?((?:\d+|[A-Z])\.?(?:\d+)?)',line1,flags=re.IGNORECASE):
#                     mo1=re.search(r'tab(?:le)?\.? ?((?:\d+|[A-Z])\.?(?:\d+)?\.?) ?(.*)',line1,flags=re.IGNORECASE)
#                     num=mo1.group(1) # 序号
#                     cap=mo1.group(2) # 图注
#                     if not re.search(r"^([A-Z]|\$|\().*",cap): # 不是大写字母开头，说明不是题注，慎用。
#                         cap=line1.strip() 
#                     tex[idx1]="" # 清空原题注行
#                     fmt_tab = insert_tex(fmt_tab,'label','tab'+num)
#                     fmt_tab = insert_tex(fmt_tab,'caption',cap.strip())
#                     break

#             if r"\begin{center}" in tex[tabular_begin-1]:
#                 tex[tabular_begin-1]=""
#             if r"\end{center}" in tex[tabular_end+1]:
#                 tex[tabular_end+1]=""

#             tex=tex[:tabular_begin]+fmt_tab+tex[tabular_end+1:]
#             idx+=len(fmt_tab)
#         else:
#             idx+=1
#     return tex


def modify_stitch(tex:list[str]):
    floater = r'(figure|table)'
    

    for loop in [1,2,3]: # 三次循环，确保所有的浮动体都被处理
        idx_docubegin=FindFirst(r"==document boby begins",tex)
        idx_docuend=FindFirst(r"==document body ends",tex)
        
        # 是否在环境中    
        flag_data=[1] *len(tex)
        flag=0
        for i in range(idx_docubegin,idx_docuend+1):
            flag += len(re.findall(r'\\begin{.*?}',tex[i])) -len(re.findall(r'\\end{.*?}',tex[i]))
            flag_data[i] = flag
        
        idx=idx_docubegin
        while idx < idx_docuend:
            # if "First, using the non-rigid model," in tex[idx]:
            #     pass
        
            if re.search(r'\\begin\{'+floater+r'\}',tex[idx]):
                # 找到一个给定浮动体，确定其始末位置
                isabort=0
                floater_begin=idx
                floater_end=FindFirst(r'\\end\{'+floater+r'\}',tex[idx+1:])+idx+1

                # 找到浮动体前后的段落的位置
                # flag=0
                floaterflag=0
                isfound_before=0
                for before_idx in range(floater_begin-1,max(floater_begin-10,idx_docubegin),-1):
                    # flag += len(re.findall(r'\\begin{.*?}',tex[before_idx])) -len(re.findall(r'\\end{.*?}',tex[before_idx]))
                    floaterflag += len(re.findall(r'\\begin{'+floater+r'}',tex[before_idx])) -len(re.findall(r'\\end{'+floater+r'}',tex[before_idx]))
                    if flag_data[before_idx]==0 and re.search(r'^\w',tex[before_idx].strip()):  # 不在环境中，且是字母开头，说明是一个段落
                        isfound_before=1
                        break
                    if floaterflag==0 and flag_data[before_idx]!=0:
                        isabort=1   # 检索到别的环境了，说明不应该继续了
                    
                # flag=0
                floaterflag=0
                isfound_behind=0
                for behind_idx in range(floater_end+1,min(floater_end+100,idx_docuend)):
                    # flag += len(re.findall(r'\\begin{.*?}',tex[behind_idx])) -len(re.findall(r'\\end{.*?}',tex[behind_idx]))
                    floaterflag += len(re.findall(r'\\begin{'+floater+r'}',tex[behind_idx])) -len(re.findall(r'\\end{'+floater+r'}',tex[behind_idx]))
                    if flag_data[behind_idx]==0 and re.search(r'^[\w\$]',tex[behind_idx].strip()):  # 不在环境中，且是字母开头，说明是一个段落
                        isfound_behind=1
                        break
                    if floaterflag==0 and flag_data[behind_idx]!=0:
                        isabort=1   # 检索到别的环境了，说明不应该继续了
                        
                if isfound_before and isfound_behind and not isabort:
                    # 下面看前后段落是不是应该拼接起来
                    tex[before_idx]=re.sub(r"\\$","",tex[before_idx].strip())+"\n" # 删除末尾的「\\」
                    tex[behind_idx]=re.sub(r"\\$","",tex[behind_idx].strip())+"\n" # 删除末尾的「\\」
                    
                    if re.search(r'[\.\:] ?(\(.*\)|\[.*\])?$',tex[before_idx].strip()) and re.search(r'^[A-Z]',tex[behind_idx].strip()):
                        pass  # 如果前段落的末尾是句号or冒号（忽略括号）、且后段落的起始是大写字母，则不拼接
                    elif re.search(r'^\\.*\{.*\}',tex[behind_idx].strip()) or re.search(r'^\\.*\{.*\}',tex[before_idx].strip()):
                        pass  # 如果前后段有一个是命令环境（章节标题/公式），则不拼接
                    elif re.search(r"^\$",tex[before_idx].strip()): # 如果前段落是行内公式，则不拼接
                        pass
                    elif r"% ==" in tex[behind_idx] or r"% ==" in tex[before_idx]:
                        pass # 如果前后段有一个是「% ==」这样的位点，则不拼接
                    else:  # 其它情况都拼接。
                        gathered=tex[before_idx].strip() + ' ' +tex[behind_idx].strip()
                        tex[before_idx]=gathered+'\n'
                        tex[behind_idx]='% ==AUTO MOVED \n'

                idx=behind_idx+1
            
            elif flag_data[idx]==0: # 普通正文环境
                # if r"\begin{" in tex[idx]:   # 跳过其他环境
                #     endidx=FindFirst(r"\\end\{",tex[idx:])+idx
                #     idx=endidx+1
                
                if re.search(r'\w+',tex[idx]) and re.search(r'^ *[a-z]',tex[idx+1]) and not "% ==" in tex[idx] and not "% ==" in tex[idx+1]:
                    # 一行有字，而下一行以小写字母开头，同时二者都不是注释点位行，则拼接
                    line : str = tex[idx]
                    line=line.strip()
                    line=re.sub(r'\\+\[0pt\]?$',"",line).strip()   # 删去末尾的「\\」，若有
                    flag=1
                    if re.search(r'-$',line):   # 如果最后一个字符是连字符，说明把一个单词劈开了
                        flag=0
                        line=re.sub(r'-$',"",line)  # 删去
                    
                    tex[idx] = line + " "*flag + tex[idx+1].strip() + "\n"
                    tex[idx+1] = "\n"
                    
                else: # 普通正文
                    tex[idx]=re.sub(r"\\\\$","",tex[idx].strip())+"\n" # 删除末尾的「\\」
                    tex[idx]=re.sub(r"\w *\\\\ *\w","",tex[idx]) # 删除中间的的「\\」
                    
                idx += 1
                
            else: # 大概是在某个环境内部，不做处理
                idx+=1
        
        
    
    # 再次检查，标记可疑位点
    idx=FindFirst(r"==document boby begins",tex)
    idx_end=FindFirst(r"==document body ends",tex)
    cnt=0
    flag=0
    listflag=0
    while idx < idx_end:
        tex[idx] =re.sub(r"\\\\ *\}","}",tex[idx])
        
        line : str = tex[idx]

        flag += len(re.findall(r'\\begin{.*?}',line)) - len(re.findall(r'\\begin{itemize}|\\begin{enumarate}',line))  #子环境层数，但不包括列表环境

        if flag==0: # 非子环境内（或在列表环境内）
            if not re.search(r"^[ \t]*(?:$|[A-Z]|where|\\[a-zA-Z]|%|\\item)",line) : # 不是{空行or大写字母or「where」or命令or注释符号or\item}开头，可能是错误断段
                backcheckidx=idx-1
                while re.match(r"^[ \t]*$",tex[backcheckidx]): # 是空行，就继续往上找
                    backcheckidx -= 1
                if not re.search(r"\\end\{align",tex[backcheckidx]):  # 如果找到的第一个非空行，是公式的结尾「\end{align」，则什么也不做
                    tex[idx]=line.strip() + "\n   % == ↑↑ CHECK HERE! 也许是错误断段\n"    # 否则，可能是错误断段
                    cnt+=1
            if not (re.search(r"[\.,\:\?\!]$|",line.strip()) or len(line.strip())==0 ): # 不是{标点符号结尾or空行}
                aftercheckidx=idx+1
                while re.match(r"^[ \t]*$",tex[aftercheckidx]): # 是空行，就继续往下找
                    aftercheckidx += 1
                if not re.search(r"\\begin\{",tex[aftercheckidx]): # 如果找到的第一个非空行，是环境的开头，则什么也不做
                    tex[idx]= " % == ↓↓ CHECK HERE! 也许是错误断段\n" + line.strip()   # 否则，可能是错误断段
                    cnt+=1
            if re.search(r"\\footnotetext",line): # 脚注
                tex[idx]="% == ↓↓ CHECK HERE! 最好不要用footnote\n"+line
                cnt+=1
        
            
        
        flag -= len(re.findall(r'\\end{.*?}',line)) - len(re.findall(r'\\end{itemize}|\\end{enumarate}',line))
        idx += 1
    
    print(f"[**]正文中有 {cnt} 处可能异常，已标注「CHECK HERE!」，请注意检查")
    logging.warning(f"排版完成，正文中有 {cnt} 处可能异常，已标注「CHECK HERE!」")
    
    return tex

def modify_sectiontitle(tex):
    idx_begin=FindFirst(r"==document boby begins",tex)
    idx_end=FindFirst(r"==document body ends",tex)
    for i in range(idx_begin,idx_end+1):
        tex[i]=re.sub(r'\\(?:sub)*section\*\{\d+\.\d+\.\d+\.? *(.*)\}',r'\\subsubsection{\1}',tex[i])
        tex[i]=re.sub(r'\\(?:sub)*section\*\{\d+\.\d+\.? *(.*)\}',r'\\subsection{\1}',tex[i])
        tex[i]=re.sub(r'\\(?:sub)*section\*\{\d+\.? *(.*)\}',r'\\section{\1}',tex[i])
        
        
        
    return tex

        
def ItIsABook(tex):  # 简单小替换
    for idx,line in enumerate(tex):
        line=re.sub(r'\\documentclass\[.*\]\{.*\}',r'\\documentclass[utf8]{ctexbook}',line)
        line=line.replace(r'\maketitle','')
        line=line.replace(r'\section{',r'\chapter{')
        line=line.replace(r'\subsection{',r'\section{')
        line=line.replace(r'\subsubsection{',r'\subsection{')
        line=re.sub(r'\\.*{references?}',r'\\section{References}',line,flags=re.IGNORECASE)

        tex[idx]=line
    

    return tex

            

    # sf1 = r'\begin{figure}'
    # sf2 = r'\end{figure}'
    # st1 = r'\begin{table}'
    # st2 = r'\end{table}'
    # sg1 = r'\begin'
    # sg2 = r'\end'

    # i = 0
    # L = len(tex)
    # while i<L:
    #     if sf1 in tex[i] or st1 in tex[i]:
    #         for j in range(i,L):
    #             if sf2 in tex[j] or st2 in tex[j]:
    #                 break
            
    #         flag_text = True
    #         for k in range(i-1,0,-1):
    #             if sg2 in tex[k]:
    #                 flag_text = False
    #             if sg1 in tex[k]:
    #                 flag_text = True
    #                 continue
    #             if flag_text and len(tex[k])>2:
    #                 index_1 = k
    #                 break

    #         flag_text = True
    #         for k in range(j+1,L):
    #             if sg1 in tex[k]:
    #                 flag_text = False
    #             if sg2 in tex[k]:
    #                 flag_text = True
    #                 continue
    #             if flag_text and len(tex[k])>2:
    #                 index_2 = k
    #                 break
    #         tex[index_1] = tex[index_1].strip()+tex[index_2]
    #         tex = tex[:index_2]+tex[index_2+1:]
    #         i = index_2+1
    #         L = len(tex)
    #     else:
    #         i += 1
    # return tex

import re

def FindFirst(pat,lst,flg=0):  #找到字符串数组lst中第一次正则匹配到pat的索引位置
    try:
        i=lst.index(next(filter(re.compile(pat,flags=flg).search,lst)))
    except StopIteration: # 一个也没找到
        i=None
    return i


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

def create_new_tex(tex_template):
    end_idx=FindFirst(r'\\end{document}',tex_template)
    return tex_template[0:end_idx+1]

def modify_title(tex_0,tex_1):
    title=''
    title_idx=FindFirst(r'\\title{.*?}',tex_0) 
    if title_idx:
        title=re.search(r'\\title{(.*?)}',tex_0[title_idx]).group(1)
        print('标题:',title)
    
    title_idx1=FindFirst(r'\\title{(.*)}',tex_1)
    if title_idx1:
        tex_1[title_idx1]=r'\title{'+title+'}\n'   # 若模板里有标题栏，则插入

    return tex_1
    

def modify_author(tex_0,tex_1):
    author=""
    author_idx=FindFirst(r'\\author{',tex_0)
    if author_idx: # 如有作者
        aths_raw=re.search(r'\\author{(.*)}?',tex_0[author_idx]).group(1).replace("}","")
        aths_raw=re.sub(r'\$.*\$','',aths_raw) # 删去可能的角标
        aths=aths_raw.split(',')
        for i,ath in enumerate(aths):
            author=author+ath
            if i<2: # 最多三个作者
                author=author+', '
            else: # 后面的省略
                author=author+" et al."
                break
        print("作者："+author)
    
    author_idx1=FindFirst(r'\\author{(.*)}',tex_1)
    if author_idx1:
        tex_1[author_idx1]=r'\author{'+author+'}\n' # 若模板里有作者栏，则插入

    return tex_1


def modify_abstract(tex_0,tex_1):
    abstract=""
    abstract_idx=FindFirst(r'\\begin{abstract}',tex_0)
    insert_idx=FindFirst(r'\\begin{abstract}',tex_1)
    
    if abstract_idx and insert_idx: # 如有摘要，则插入
        abstract = tex_0[abstract_idx+1]
        tex_1.insert(insert_idx+1,abstract)
    return tex_1


def modify_body(tex_0,tex_1):

    start_idx=FindFirst(r'\\end{abstract}',tex_0) # 寻找正文开始处
    if not start_idx:
        start_idx=FindFirst(r'\\begin{document}',tex_0) # 保底

    end_idx=FindFirst(r'{references}|{acknowledgments}',tex_0,flg=re.I) # 寻找正文结束处
    if not end_idx:
        end_idx=FindFirst(r'\\end{document}',tex_0) # 保底

    body = tex_0[start_idx+1:end_idx-1]

    insert_idx=FindFirst(r'==document body here',tex_1) # 在新文档中插入正文
    # if not insert_idx:
    #     insert_idx=FindFirst(r'\\end{document}',tex_1)-1 # 保底
    tex_1_new=tex_1[:insert_idx]+body+tex_1[insert_idx+1:]

    return tex_1_new

def get_suffix(tex_0): # 把参考文献那些摘除，等翻译完再接回来
    suffix=""
    ref_idx=FindFirst(r'{references}|{acknowledgments}',tex_0,flg=re.I)
    end_idx=FindFirst(r'\\end{document}',tex_0)
    if ref_idx and end_idx:
        suffix=''.join(tex_0[ref_idx:end_idx-1])
    return suffix


def modify_equation(tex,format_equation):
    idx=0
    while idx<len(tex):
        line=tex[idx]
        if '$$' in line:
            start_idx=idx
            end_idx=FindFirst(r'\$\$',tex[start_idx+1:])+start_idx+1

            fmt_eqn=format_equation.copy()
            insert_idx=FindFirst("==here",fmt_eqn)
            fmt_eqn=fmt_eqn[:insert_idx]+tex[start_idx+1:end_idx]+fmt_eqn[insert_idx+1:]

            tex=tex[:start_idx]+fmt_eqn+tex[end_idx+1:]
            # 为什么不用管第二个$$：因为end_idx已经找到了第二个$$，通过tex[end_idx+1:]已经把它排除了              
        idx+=1
    
    return tex
    

def modify_figure(tex,format_figure):
    idx=0
    while idx<len(tex):
        line=tex[idx]
        mo=re.search(r'\\includegraphics\[.*\]{(.*)}',line)
        if mo:
            file=mo.group(1)    # 文件名
            for idx1,line1 in enumerate(tex[idx:]):
                if re.search(r'fig',line1,flags=re.IGNORECASE):
                    mo1=re.search(r'fig(?:ure)?\.? ?((?:\d+)\.?(?:\d+)?) ?(.*)',line1,flags=re.IGNORECASE)
                    num=mo1.group(1) # 序号
                    cap=mo1.group(2) # 图注
                    break
            fmt_fig=format_figure.copy()
            fmt_fig = insert_tex(fmt_fig,'label','fig'+num)
            fmt_fig = insert_tex(fmt_fig,'caption',cap)
            fmt_fig = insert_tex(fmt_fig,'includegraphics',file)

            tex=tex[:idx-1]+fmt_fig+tex[idx+idx1+1:]
            idx+=len(fmt_fig)
        else:
            idx+=1
    return tex


def modify_table(tex,format_table):
    s1 = r'\begin{tabular}'
    s2 = r'\end{tabular}'
    sh = r'\hline'
    sf = r'Table'
    sfx = r'TABLE'
    sl = r'{'
    sr = r'}'
    #删掉\begin{center}，\end{center}格式
    sp1 = r'\begin{center}'
    sp2 = r'\end{center}'

    i = 0
    L = len(tex)
    while i<L:
        if s1 in tex[i]:
            index_start = i
            #找格式
            line_tformat = tex[i]
            l_idx = line_tformat.rfind(sl)
            r_idx = line_tformat.rfind(sr)
            tformat = line_tformat[l_idx+1:r_idx]
            tformat = tformat.replace('|','')

            for j in range(i,L):
                if s2 in tex[j]:
                    index_end = j
                    break
            if sp1 in tex[index_start-1]:
                index_start -= 1
            if sp2 in tex[index_end+1]:
                index_end += 1   

            #找表名
            for k in range(index_start,0,-1):
                if sf in tex[k] or sfx in tex[k]:
                    line_title = tex[k]
                    break
            sf_idx = line_title.rfind(sf)
            sfx_idx = line_title.rfind(sfx)
            s_idx = max(sf_idx,sfx_idx)
            L_line = len(line_title)
            for c_idx in range(s_idx,L_line):
                if line_title[c_idx] == '.':
                    t_idx = c_idx+1
                    break
            title = line_title[t_idx:].strip()
            tex[k] = line_title[0:s_idx]

            #找表头
            k = index_start+1
            flag_head = False
            while k<index_end:
                if sh in tex[k]:
                    flag_head = True
                    k += 1
                    continue
                if flag_head:
                    index_head = k
                    head = tex[k]
                    break
                k += 1
            #找表的内容
            k = index_head+1
            content = []
            while k<index_end-1:
                if sh in tex[k]:
                    k+= 1
                    continue
                content.append(tex[k])
                k+= 1
            
            #套用格式
            formatted_table = format_table.copy()
            formatted_table[2] = formatted_table[2].replace('Table Title',title)
            formatted_table[3] = formatted_table[3].replace('ccc',tformat)
            formatted_table = formatted_table[0:5]+[head]+[formatted_table[6]]+content+formatted_table[8:]
            tex = tex[:index_start-1]+formatted_table+tex[index_end+1:]
            i = index_start+len(formatted_table)
            L = len(tex)
        else:
            i += 1
    return tex

def modify_stitch(tex):
    sf1 = r'\begin{figure}'
    sf2 = r'\end{figure}'
    st1 = r'\begin{table}'
    st2 = r'\end{table}'
    sg1 = r'\begin'
    sg2 = r'\end'

    i = 0
    L = len(tex)
    while i<L:
        if sf1 in tex[i] or st1 in tex[i]:
            for j in range(i,L):
                if sf2 in tex[j] or st2 in tex[j]:
                    break
            
            flag_text = True
            for k in range(i-1,0,-1):
                if sg2 in tex[k]:
                    flag_text = False
                if sg1 in tex[k]:
                    flag_text = True
                    continue
                if flag_text and len(tex[k])>2:
                    index_1 = k
                    break

            flag_text = True
            for k in range(j+1,L):
                if sg1 in tex[k]:
                    flag_text = False
                if sg2 in tex[k]:
                    flag_text = True
                    continue
                if flag_text and len(tex[k])>2:
                    index_2 = k
                    break
            tex[index_1] = tex[index_1].strip()+tex[index_2]
            tex = tex[:index_2]+tex[index_2+1:]
            i = index_2+1
            L = len(tex)
        else:
            i += 1
    return tex
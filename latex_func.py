import re
#在tex_file中找到st,并在st的{}中插入content
def insert_tex(tex_file,st,content):
    for line_idx, line in enumerate(tex_file):
        if st in line:
            insert_line = line
            insert_idx = line_idx
            break
    for c_idx,c in enumerate(insert_line):
        if c=='{':
            k_idx = c_idx+1
            break
    new_line = insert_line[:k_idx]+content+insert_line[k_idx:]
    tex_file[insert_idx] = new_line
    return tex_file

def get_format_figure(tex_file):
    head = r'\begin{figure}'
    tail = r'\end{figure}'
    head_idx = 0
    tail_idx = 1
    for line_idx, line in enumerate(tex_file):
        if head in line:
            head_idx = line_idx
        if tail in line:
            tail_idx = line_idx
            break
    return tex_file[head_idx:tail_idx+1]

def get_format_equation(tex_file):
    head = r'\begin{dmath}'
    tail = r'\end{dmath}'
    head_idx = 0
    tail_idx = 1
    for line_idx, line in enumerate(tex_file):
        if head in line:
            head_idx = line_idx
        if tail in line:
            tail_idx = line_idx
            break
    return tex_file[head_idx:tail_idx+1]

def get_format_table(tex_file):
    head = r'\begin{table}'
    tail = r'\end{table}'
    head_idx = 0
    tail_idx = 1
    for line_idx, line in enumerate(tex_file):
        if head in line:
            head_idx = line_idx
        if tail in line:
            tail_idx = line_idx
            break
    return tex_file[head_idx:tail_idx+1]

def create_new_tex(tex_file):
    end = r'\end{document}'
    end_idx = 1
    for line_idx, line in enumerate(tex_file):
        if end in line:
            end_idx = line_idx
            break
    return tex_file[0:end_idx+1]

def modify_title(tex_file_0,tex_file):
    st = r'\title'
    sl = r'{'
    sr = r'}'

    for line_idx, line in enumerate(tex_file_0):
        if st in line:
            line_title = line
            break
    for c_idx,c in enumerate(line_title):
        if c==sl:
            idx_l = c_idx
        if c==sr:
            idx_r = c_idx
    while(line_title[idx_r-1]==' '):
        idx_r-= 1
    title = line_title[idx_l+1:idx_r]
    s_tile = r'\title{}'
    print('标题:',title)
    return insert_tex(tex_file,s_tile,title)

def modify_author(tex_file_0,tex_file):

    for line in tex_file_0:
        mo=re.search(r'\\author{(.*)',line)
        if mo:
            aths_raw=mo.group(1)
            aths_raw=re.sub(r'\$.*\$','',aths_raw) # 删去可能的角标
            aths=aths_raw.split(',')
            author=""
            for i,ath in enumerate(aths):
                author=author+ath
                if i<2: # 最多三个作者
                    author=author+', '
                else: # 后面的省略
                    author=author+" et al."
                    break
            break
    print("作者："+author)
    
    for idx,line in enumerate(tex_file):
        if re.search(r'\\author{(.*)}',line):
            tex_file[idx]=r'\author{'+author+'}\n'
            break
    
    return tex_file





def modify_abstract(tex_file_0,tex_file):
    st = r'\begin{abstract}'
    for line_idx, line in enumerate(tex_file_0):
        if st in line:
            abstract_idx = line_idx+1
            break
    abstract = tex_file_0[abstract_idx]
    for line_idx, line in enumerate(tex_file):
        if st in line:
            insert_idx = line_idx+1
            break
    #print(abstract)
    tex_file.insert(insert_idx,abstract)
    return tex_file

def modify_references(tex_file_0,tex_file):
    st = r'{References}'
    stx = r'{REFERENCES}'
    se = r'\end{document}'
    st3 = r'[1]'
    flag_ref = False
    for line_idx, line in enumerate(tex_file_0):
        if st in line or stx in line:
            flag_ref = True
            ref_idx = line_idx+1
        if se in line:
            end_idx = line_idx-1
            break
    
    if not flag_ref:
        for line_idx, line in reversed(list(enumerate(tex_file_0))):
            if st3 in line:
                ref_idx = line_idx

    ref = tex_file_0[ref_idx:end_idx]
    for line_idx, line in enumerate(tex_file):
        if st in line:
            insert_idx = line_idx+1
            break
    return tex_file[:insert_idx]+ref+tex_file[insert_idx:]

def modify_body(tex_file_0,tex_file):
    st0 = r'\end{abstract}'
    st1 = r'\section'
    st2 = r'{References}'
    st2x = r'{REFERENCES}'
    st2xx=r'{ACKNOWLEDGMENTS}'
    st3 = r'[1]'
    flag_ref = False
    for line_idx, line in enumerate(tex_file_0):
        if st0 in line:
            start_idx = line_idx+1
            continue
        if re.search(r'{references}|{acknowledgments}',line,flags=re.IGNORECASE):
            flag_ref = True
            end_idx = line_idx-1
            break

    if not flag_ref:
        for line_idx, line in reversed(list(enumerate(tex_file_0))):
            if st3 in line:
                end_idx = line_idx-1
                break

    body = tex_file_0[start_idx:end_idx]

    for line_idx, line in enumerate(tex_file):
        if st2 in line:
            insert_idx = line_idx-1

    suffix=''.join(tex_file_0[end_idx:-2])
    # with open('suffix.txt','w') as f:
    #     f.write(''.join(tex_file_0[end_idx:-2]))

    
    return tex_file[:insert_idx]+body+tex_file[insert_idx:],suffix

def modify_equation(tex,format_equation):
    st0 = r'$$'
    st1 = r'\begin{aligned}'
    st2 = r'\begin{array}'
    st3 = r'\begin{gathered}'
    stx = r'\\'

    i = 0
    L = len(tex)
    while i<L:
        if st0 in tex[i]:
            start = i+1 
            for j in range(start,L):
                if st0 in tex[j]:
                    end = j-1
                    break
            if st1 in tex[start] or st2 in tex[start] or st3 in tex[start]:
                start = start+1
                end = end-1
            #print(start+1,end+1)
            #套用格式
            k = start
            formatted_equation = []
            while k<= end:
                equation = tex[k]
                equation = equation.replace('&','')
                equation = equation.replace(stx,'') 
                equation = equation.strip()
                format_copy = format_equation.copy()
                format_copy.insert(1,equation+'\n')
                formatted_equation = formatted_equation+format_copy
                k += 1
            tex = tex[:i]+formatted_equation+tex[j+1:]
            i += len(formatted_equation)
            L = len(tex)
        else:
            i += 1
    return tex

def modify_figure(tex,format_figure):
    si = r'\includegraphics'
    sf = r'Figure'
    sfx = r'FIG'
    sfxx = r'Fig'
    sl = r'{'
    sr = r'}'

    #删掉\begin{center}，\end{center}格式
    sp1 = r'\begin{center}'
    sp2 = r'\end{center}'

    i = 0
    L = len(tex)
    while i<L:
        if si in tex[i]:
            start = i+1
            line_file = tex[i]
            for c_idx,c in enumerate(line_file):
                if c==sl:
                    idx_l = c_idx
                if c==sr:
                    idx_r = c_idx
            file = line_file[idx_l+1:idx_r]

            for j in range(start,L):
                if sf in tex[j] or sfx in tex[j] or sfxx in tex[j]:
                    line_title = tex[j]
                    break
            for c_idx,c in enumerate(line_title):
                if c.isdigit():
                    idx_d = c_idx+1
                    num = c
                    while line_title[idx_d].isdigit():
                        num = num + line_title[idx_d]
                        idx_d += 1
                    while line_title[idx_d] == '.' or line_title[idx_d] == ' ':
                        idx_d += 1
                    break
            title = line_title[idx_d:].strip()
            label = 'figure'+num
            # print(label)
            # print(file)
            # print('figure:'title)
            #套用格式
            formatted_figure = format_figure.copy()
            formatted_figure = insert_tex(formatted_figure,'label',label)
            formatted_figure = insert_tex(formatted_figure,'caption',title)
            formatted_figure = insert_tex(formatted_figure,'includegraphics',file)
            if sp1 in tex[i-1]:
                i -= 1
            tex = tex[:i]+formatted_figure+tex[j+1:]
            i += len(formatted_figure)
            L = len(tex)
        else:
            i += 1
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
import typeset_func2 as lf
from tkinter import filedialog
import os,json

def open_file():
    # ========打开文件=========
    print("<< 请打开从Mathpix导出的tex文档...")
    f_path = filedialog.askopenfilename(initialdir='./',filetypes=(('tex files','*.tex'),))
    if not f_path:
        exit()
    (basedir,filename)=os.path.split(f_path)
    
    with open('filepath.txt', 'w', encoding='utf-8') as f:
        json.dump({'basedir':basedir,'filename':filename},f)

    return basedir,filename

def TYPESET(basedir,filename):

    input_file_path = basedir+'/'+filename
    template_file_path = 'template.tex'
    typeset_file_path = basedir+'/[排版]'+filename

    # =======处理文件===========
    print(">> 开始排版预处理...")
    with open(input_file_path, 'r',encoding='utf-8') as file_0:
        tex_0 = file_0.readlines()
    with open(template_file_path, 'r',encoding='utf-8') as file_1:
        tex_template = file_1.readlines()

    format_figure = lf.get_format_figure(tex_template)
    format_equation = lf.get_format_equation(tex_template)
    format_table = lf.get_format_table(tex_template)
    tex_1 = lf.create_new_tex(tex_template)

    tex_1 = lf.modify_title(tex_0,tex_1)
    tex_1 = lf.modify_author(tex_0,tex_1)
    tex_1 = lf.modify_abstract(tex_0,tex_1)
    tex_1 = lf.modify_body(tex_0,tex_1)
    suffix=lf.get_suffix(tex_0)
    # tex_1 = lf.modify_suffix(tex_0,tex_1)

    tex_1 = lf.modify_equation(tex_1,format_equation)
    tex_1 = lf.modify_figure(tex_1,format_figure)
    tex_1 = lf.modify_table(tex_1,format_table)
    # tex_1 = lf.modify_stitch(tex_1)

    with open(typeset_file_path, 'w',encoding='utf-8') as file_2:
        file_2.write(' '.join(tex_1))
    with open(basedir+"/suffix.txt",'w',encoding='utf-8') as f:
        f.write(suffix)

    print('>> 已保存到：'+typeset_file_path)
    path1=typeset_file_path.replace('/','\\')
    os.system(f"C:\Windows\explorer.exe /select, {path1}")

    print("\n>> 请编译排版后的tex进行检查，特别是：\n1. 公式是否正确，例如编号、多行；\n2. 跨页处是否错误地分了段；\n3. 脚注是否被混进了正文段落。")

if __name__=="__main__":
    basedir,filename=open_file()
    TYPESET(basedir,filename)

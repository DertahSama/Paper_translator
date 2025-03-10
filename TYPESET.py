import typeset_func2 as lf
from tkinter import filedialog
import os,json,zipfile,yaml,logging,datetime

def UnZIP(zip_name, realname=None, savedir=None):
    # 解压
    (pname,fname)=os.path.split(zip_name)
    if not savedir: savedir=pname
    if not realname: realname=os.path.splitext(fname)[0]

    with zipfile.ZipFile(zip_name) as f:
        given_name=f.namelist()[0].replace('/','')  # mathpix给这个转换任务起的名字
        # print(given_name)
        f.extractall(savedir)

    realname1=realname
    i=1
    while os.path.exists(f'{savedir}/{realname1}'):
        realname1=realname+f"({i})"
        i+=1
    os.rename(f'{savedir}/{given_name}',f'{savedir}/{realname1}')
    os.rename(f'{savedir}/{realname1}/{given_name}.tex',f'{savedir}/{realname1}/{realname}.tex')

    # with open('filepath.txt', 'w', encoding='utf-8') as f:
    #     json.dump({'basedir':f'{savedir}/{realname}','filename':f'{realname}.tex'},f,indent=4, ensure_ascii=False)

    return f'{savedir}/{realname1}',f'{realname}.tex'
    

def open_file():
    # ========打开文件=========
    # with open('config.json',encoding='utf8') as f: config=json.load(f)
    with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)

    if config["排版设置"]["处理filepath里储存的文件名"]:
        print("[*] 正在处理filepath.txt里储存的文件名")
        with open('filepath.txt', 'r',encoding='utf-8') as f:
            file=json.load(f)
        basedir=file["basedir"]
        filename=file["filename"]
        print(basedir+r'/'+filename)
    else:
        # print("<< 请打开从Mathpix导出的tex文档...")
        # f_path = filedialog.askopenfilename(initialdir='./',filetypes=(('tex files','*.tex'),))
        # if not f_path:
        #     exit()
        # (basedir,filename)=os.path.split(f_path)
        
    
        print(">> 请打开从Mathpix导出的zip文档...")
        f_path = filedialog.askopenfilename(initialdir='./',filetypes=(('zip files','*.zip'),))
        print(f_path)
        if not f_path:
            exit()

        basedir,filename=UnZIP(f_path)
        with open('filepath.txt', 'w', encoding='utf-8') as f:
            json.dump({'basedir':basedir,'filename':filename},f,indent=4, ensure_ascii=False)

    return basedir,filename

def TYPESET(basedir,filename):
    logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
    with open('filepath.txt', 'w', encoding='utf-8') as f:
            json.dump({'basedir':basedir,'filename':filename},f,indent=4, ensure_ascii=False)
    # with open('config.json',encoding='utf8') as f: config=json.load(f)
    with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)

    input_file_path = basedir+'/'+filename
    template_file_path = 'template.tex'
    typeset_file_path = basedir+'/[排版]'+filename

    # =======处理文件===========
    print("[*] 开始排版预处理...")
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
    
    tex_1 = lf.modify_pre(tex_1)

    tex_1 = lf.modify_equation1(tex_1,format_equation)
    tex_1 = lf.modify_figure(tex_1,format_figure)
    tex_1 = lf.modify_table1(tex_1,format_table)


    if config['排版设置']['这是一本书']:
        tex_1 = lf.ItIsABook(tex_1)
        suffix=''
    else:
        tex_1, suffix=lf.get_suffix(tex_1)  # 抽离参考文献
    with open(basedir+"/suffix.txt",'w',encoding='utf-8') as f:
        f.write(suffix)
        
    tex_1 = lf.modify_stitch(tex_1) # 检查并拼接浮动体前后的段落

    tex_1 = lf.modify_sectiontitle(tex_1)

    with open(typeset_file_path, 'w',encoding='utf-8') as file_2:
        file_2.write(' '.join(tex_1))

    

    if config['排版设置']['立即编译所得tex']:
        print("\n[*] 编译排版后的tex文件中……\n")
        cmd=f'cd /d \"{basedir}\" '\
            '&& '\
            f'xelatex.exe -synctex=1 -interaction=batchmode -halt-on-error '\
                f'\"{typeset_file_path}\"'
        os.system(cmd)
        logging.warning("[排版]已编译为PDF文件")


    print('\n>> 已保存到：'+typeset_file_path)
    path1=typeset_file_path.replace('/','\\')
    os.system(f'C:/Windows/explorer.exe /select, "{path1}"')
    print("\n>> 请编译排版后的tex进行检查，特别是：\n1. 公式是否正确，例如编号、多行；\n2. 跨页处是否错误地分了段；\n3. 脚注是否被混进了正文段落。")

if __name__=="__main__":
    logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
    basedir,filename=open_file()
    logging.warning(".")
    logging.warning(".")
    TYPESET(basedir,filename)

import requests,logging
import json,time,os,sys,yaml,datetime
from tkinter import filedialog

def ProgressBar1(prgss:float):
    progress=int(prgss*50)
    print("\r进度: %.1f %%: "%(prgss*100), "▋"*progress + "-"*(50-progress), end="")
    if prgss==1:
        print("done！")   #100%了换个行
    sys.stdout.flush()
    time.sleep(0.001)
    
def ProgressBar(now : int, alls : int):
    '''
    根据输入的当前值和总数值打印一个进度条。100%前不换行，下一次打印时将覆盖本行；100%后换行。
    :param now:     当前值
    :param alls:    总数值
    '''
    progress=int(now/alls*50)
    print("\r进度: % 3d/% 3d: "%(now,alls), "▋"*progress + "-"*(50-progress), end="")
    if now==alls:
        print("done！")   #100%了换个行
    sys.stdout.flush()
    time.sleep(0.001)


def pdf_download(mypdfid,fname="sth"):
    # 因为任何原因，需要用pdf_id手动下载zip的情形
    # 2025-03-12 12-33-14
    with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)
    for apidir in config["翻译设置"]["翻译APIkeys文件夹"]:
        if os.path.exists(apidir):
            print("[**] 读取API："+apidir+'/mathpix_keys.yaml')
            break
    with open(apidir+'/mathpix_keys.yaml', 'r',encoding="utf8") as file: keys=yaml.load(file,Loader=yaml.Loader)
    myheader={
            "app_id": keys["app_id"],
            "app_key": keys["app_key"]
        }
    
    while 1:
        r = requests.get("https://api.mathpix.com/v3/pdf/"+mypdfid,headers=myheader)
        rtext=json.loads(r.text)
        if "num_pages_completed" in rtext:
            ProgressBar(rtext["num_pages_completed"],rtext["num_pages"])
        else:
            print("别急…",end="")
        
        if rtext["status"]=="completed":
            break
        time.sleep(0.5)

    toshow=f"耗费页数：{rtext['num_pages']}，计费{rtext['num_pages']*0.005*7.2:,.3f}元" 
    print(toshow+"    下载中……")
    logging.warning(toshow)

    # get LaTeX zip file
    savepath = os.path.abspath(config["PDF识别设置"]["保存路径"])
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    zipname:str = fname + ".zip"
    zipname =savepath + "\\" +zipname
    zipname1=zipname
    i=1
    while os.path.exists(zipname1):
        zipname1=zipname.replace(".zip",f"({i}).zip")
        i+=1
    zipname=zipname1

    url = "https://api.mathpix.com/v3/pdf/" + mypdfid + ".tex"
    response = requests.get(url, headers=myheader)
    
    with open(zipname, "wb") as f:
        f.write(response.content)
    
    print("已保存到："+ zipname)
    return zipname
    
    


def PDF_OCR():
    with open('设置.yaml', 'r',encoding="utf8") as file: config=yaml.load(file,Loader=yaml.Loader)
    logging.basicConfig(filename=f"log{datetime.datetime.now().strftime('%y%m')}.txt", level=logging.WARNING, format='[%(asctime)s] %(message)s',encoding="utf8")
    logging.warning(".")
    logging.warning(".")
    
    print(">> 请打开一个PDF（点取消来处理本地的Mathpix zip）……")
    f_path = filedialog.askopenfilename(initialdir='./',filetypes=(('pdf files','*.pdf'),))
    if not f_path:
        return None
    (fdir,fname)=os.path.split(f_path)
    fname,ext=os.path.splitext(fname)

    print(f_path)
    logging.warning(f"正在处理：{f_path}")

    prange=input(">> 请输入需要识别的页码范围，例如「1-3」or「3-」or「1,3,5」or「1-3,5」，不输入则全部上传: ")
    if not prange:
        prange="1-"
    
    tic=time.time()
  
    options = {
        "conversion_formats": {"tex.zip": True},
        "math_inline_delimiters": ["$", "$"],
        # "math_display_delimiters": [r"\begin{align*}", r"\end{align*}"],
        "include_equation_tags": True,
        "rm_spaces": True,
        "page_ranges": prange,
    }
    
    for apidir in config["翻译设置"]["翻译APIkeys文件夹"]:
        if os.path.exists(apidir):
            print("[**] 读取API："+apidir+'/mathpix_keys.yaml')
            break
    with open(apidir+'/mathpix_keys.yaml', 'r',encoding="utf8") as file: keys=yaml.load(file,Loader=yaml.Loader)
    myheader={
            "app_id": keys["app_id"],
            "app_key": keys["app_key"]
        }

    print("正在上传……")
    r = requests.post("https://api.mathpix.com/v3/pdf",
        headers=myheader,
        data={
            "options_json": json.dumps(options)
        },
        files={
            "file": open(f_path,"rb")
        }
    )
    
    mypdfid=json.loads(r.text)["pdf_id"]

    print("上传成功，pdfid = " +mypdfid+ "，正在识别……")
    logging.warning("pdfid = "+mypdfid)

    
    while 1:
        r = requests.get("https://api.mathpix.com/v3/pdf/"+mypdfid,headers=myheader)
        rtext=json.loads(r.text)
        if "num_pages" in rtext:
            if "num_pages_completed" in rtext:
                ProgressBar(rtext["num_pages_completed"],rtext["num_pages"])
            else:
                ProgressBar(0,rtext["num_pages"])
        else:
            # ProgressBar1(rtext["percent_done"]/100)
            print("别急…",end="")
            sys.stdout.flush()
        
        if rtext["status"]=="completed":
            break
        time.sleep(0.5)

    toshow=f"耗费页数：{rtext['num_pages']}，计费{rtext['num_pages']*0.005*7.2:,.3f}元" 
    print(toshow+"    下载中……")
    logging.warning(toshow)

    # get LaTeX zip file
    savepath = os.path.abspath(config["PDF识别设置"]["保存路径"])
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    zipname:str = fname + ".zip"
    zipname =savepath + "\\" +zipname
    zipname1=zipname
    i=1
    while os.path.exists(zipname1):
        zipname1=zipname.replace(".zip",f"({i}).zip")
        i+=1
    zipname=zipname1

    url = "https://api.mathpix.com/v3/pdf/" + mypdfid + ".tex"
    response = requests.get(url, headers=myheader)
    
    with open(zipname, "wb") as f:
        f.write(response.content)
    
    toc=time.time()
    print(f"[*] 识别耗时 {toc-tic:.4f} s")
    logging.warning(f"识别耗时 {toc-tic:.4f} s")
    
    print("已保存到："+ zipname)
    return zipname
    
if __name__ == "__main__":
    if 1:
        PDF_OCR()
    else:
        # 手动下载已经识别完的latex zip
        pdf_id="2025_03_11_8a702bc870bdecdc07b3g"
        fname="（Jardin,S，2010）Computational Methods in Plasma Physics"
        pdf_download(pdf_id,fname)
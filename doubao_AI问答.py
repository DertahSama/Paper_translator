# ===== 使用方法 =====
# 在用doubao翻译完一篇文章之后，直接运行本脚本即可。
# - 拥有当前文章信息的会话的id保存在「doubao-contextid.yaml」中。
# - 注意，会话是会超时过期的！超时时间在「设置.yaml」中，需要在翻译之前更改。

from volcenginesdkarkruntime import Ark
import yaml,datetime,json

with open("doubao-contextid.yaml","r",encoding="utf8") as f:
    tt=yaml.load(f,Loader=yaml.Loader)
with open('translator_keys/doubao_keys.yaml', 'r',encoding="utf8") as file: 
    keys=yaml.load(file,Loader=yaml.Loader)
with open('filepath.txt', encoding='utf-8') as f:
    file=json.load(f)
    basedir=file["basedir"]

if tt["cachemode"] == "common_prefix":
    print("[*] 当前对话的缓存模式不支持上下文问答！")
    exit()
    
print("[*] 当前会话将过期于："+tt["expiretime"]+"，每次对话会重置过期计时，请自行把握。")
print("[*] 问答将保存到："+basedir+r"\AI问答.md")

myclient = Ark(api_key=keys["api_key"])

while 1:
    print("")
    askkk=input("（输入xxx来退出）>>")
    if askkk=="xxx": break
    rsp=""
    chat_stream = myclient.context.completions.create(
        # 指定上下文ID
        context_id=tt["contextid"],
        # 指定模型
        model=keys["model"],
        # 设置消息列表，包含一个用户角色的消息
        messages=[
            {"role": "user", "content": askkk},
        ],
        # 设置为流式
        stream=True,
        )
    for chunk in chat_stream:
        if not chunk.choices:
            continue
        rsp += chunk.choices[0].delta.content
        print(chunk.choices[0].delta.content,end="")
        
    with open(basedir+r"\AI问答.md","a+",encoding="utf8") as f:
        f.writelines("\n\n.\n-------\n# "+datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S")+"\n")
        f.writelines("> "+askkk+"\n\n")
        f.writelines(rsp)

    print("")
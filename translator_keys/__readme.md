## API翻译模块简介

这里是各种可以供引用的翻译器模块，所用的API来自各个服务商的公开API，申请方法可参见：
<https://hcfy.app/docs/services/deepl>

每个api由两个文件构成：`keys.json`和`translator.py`：
- `keys.json`里面就是该服务商的API密钥，按照给定的格式填写即可。
- `translator.py`里面统一是两个函数：
  - `client=create_client()`，用来准备一个响应输入的翻译器`client`；
  - `text_zh=translator(client,text)`，利用上面准备好的`cilent`，将输入的英文`text`翻译成中文的`text_zh`。

这里写好了4个服务商的API模块，有付费的有免费的：
- chatGPT （需付费和外国信用卡）
- deepL （免费但需外国信用卡）
- 腾讯 （免费）
- 百度 （免费）
  
模块名见`translators`文件夹内。模块的导入在`translate_dunc2.py`的最开头，会在运行时让你选择。

## 各API所需要安装的包
1. 腾讯
```
pip3 install --upgrade tencentcloud-sdk-python
```
2. 百度 （并不需要专用包）
```
pip3 install requests, random, json, hashlib 
```
3. openai
```
pip3 install --upgrade openai
```
4. deepl
```
pip3 install --upgrade deepl
```
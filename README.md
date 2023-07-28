# Paper_translator
这是一个利用服务商API自动全文翻译科技论文的python脚本，需借助Mathpix识别服务。

路径：英文PDF论文→Mathpix识别→翻译（腾讯百度deepL）→中文PDF

改编自<https://github.com/Humphrey1997/Paper_trans>，这里稍加扩展改编后，打包成了exe，便于使用。

## 功能
还在硬啃英文文章吗？是时候全文翻译了！（该样例见release）
![Snipaste_2023-07-14_22-45-11](https://github.com/DertahSama/Paper_trans/assets/74524914/5dbb558c-a9c0-422d-b701-833d323f55d2)
![Snipaste_2023-07-14_23-05-14](https://github.com/DertahSama/Paper_trans/assets/74524914/e43cfd01-32e0-4c64-87d6-12391638f733)
- 全自动
- 全文翻译，中英对照
- 公式、图片、表格正确处理
- 可自定义模板

## 用法
### 获取tex文件
你需要使用Mathpix来识别pdf，生成tex文件，再送入本脚本来处理。
- 网址：<https://snip.mathpix.com>
- edu邮箱用户每月20页免费额度，再往上需要付费会员。

### 翻译服务
本脚本依靠公开的翻译服务API来工作，这里写好了四个服务的接口，这些API服务有付费的有免费的：
- chatGPT （需付费和外国信用卡）
- deepL （免费但需外国信用卡）
- 腾讯 （免费）
- 百度 （免费）

申请API方法可见<https://hcfy.app/docs/services/deepl>。

申请到密钥后，在`translator_keys`文件夹中加入自己的密钥即可，详见那里的readme。

### Latex编译pdf
这一点请自寻教程。对初学者来说，推荐texLive + TexStudio的组合。

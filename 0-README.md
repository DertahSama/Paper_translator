# Paper_trans
 translate paper to chinese  

## 实现方式  
1. 英文pdf通过mathpix转latex  
2. 插入自己的latex模板  
3. 英文latex通过chatgpt-api转中文latex  
4. 人工校对调整排版  

mathpix <https://snip.mathpix.com> 需要会员 \
如果只有少量需求，可以把文件发给我免费转换，然后自行校对  \
联系方式 hanjy19@tsinghua.org.cn  

## 使用方式  
0. 一次处理一个文件

1. 将下载好的mathpix导出的tex文档和图片文件夹放入file文件夹  \
将.tex的文件名复制放入`filename.txt`

2. 打开translators文件夹，对翻译API密钥进行设置，详见那里的`__readme.md`

3. 运行`1-TYPESET.py`进行排版，输出为1-TYPESETED.tex  
(建议翻译前确认格式没问题)  

1. 运行`2-TRANSLATE.py`进行翻译，输出为2-TRANSLATED.tex    

## changelog
- 1.0 version  \
论文的作者有时会被mathpix识别为图片，建议最后手动编辑  
如果公式在原论文中多行显示，会被识别为多个公式，导致编号问题   
由于跨页分栏，一段可能被分成两段 \
有些特殊字符会有问题，如‘Alfvén’的 ‘é’ \
图片和表格的标题没有翻译  

- 1.1 version \
添加了更多的翻译API，调整了排版

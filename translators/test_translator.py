import random,re



def create_client():
    print("[**] 假文测试！")
    class lorem_client:
        def __init__(self):
            self.translator_name="lorem"
            self.seed =["的","了","在","是","和","一","这","有","他","我","也","不","就","地","着","中","上","说","都","人","个","对","种","把","为","要","你","而","来","我们","又","一个","与","从","年","到","还","它","大","等","她","两","去","没有","里","得","时","多","他们","发展","用","那","以","所","很","可以","使","但","自己","小","之","能","下","或","看","就是","被","什么","三","这个","会","好","可","后","这样","给","向","社会","由","进行","问题","工作","如","呢","于","其","起来","国家","过","不能","并","这些","生产","生活","只","将","新","想","几","因为","不是","经济","更","研究","已","当","却","主要","再","由于","我国","最","关系","作用","不同","中国","才","人们","出","但是","现在","则","需要","所以","因此","如果","已经","一定","们","各","重要","象","一些","情况","吧","二","次","月","便","知道","时候","做","必须","成","人民","四","走","出来","活动","同","方面","条","高","吗","科学","也是","即","条件","天","许多","通过","思想","发生","叫","为了","老","过程","比","起","而且","影响","方法","要求","内","技术","点","一般","较","让","具有","形成","对于","日","事","时间","认为","还是","真","长","世界","只有","以后","教育","它们","同时","性","表现","产生","出现","企业","社会主义","作","者","没","各种","之间","家","组织","前","水","一样","成为","可能","根据","开始","吃","还有","话","存在","地方","变化","可是","革命","作为","这里","提高","五","同志","跟","以及","见","发现","及","一切","运动","呀","每","听","历史","地区","第一","物质","问","外","你们","位","正","形式","打","认识","那么","例如","学生","政治","比较","全","儿","应","第二","怎么","经过","提出","艺术","自然","头","过去","领导","完全","东西","其他","无","得到","劳动","本","谁","决定","结构","党","现象","受","理论","虽然","带","学习","孩子","特别","工业","啊","一点","建立","管理","文化","利用","先","人类","应该","建设","图","规定","有些","精神","基本","声","结果","看到","手","连","大家","时期","啦","意义","法","十","另","其中","才能","能够","分","间","当时","因","美国","解决","指","只是","语言","增加","内容","该","计划","笑","今天","相","不仅","注意","群众","联系","曾","水平","类","快","使用","写","分析","当然","既","有关","实现","此","系统","直接","不过","按","说明","产品","张","总","全国","基础","十分","市场","找","斗争","环境","特点","为什么","学","于是","反映","引起","创造","参加","甚至","讲","坐","能力","像","开","觉得","一下","民族","放","具体","知识","有的","包括","下来","部门","结合","岁","正确","任务","部分","那些","不会","任何","太","眼睛","经验","实际","随着","农业","道","极","少","不断","这时","最后","件","单位","句","数","而是","表示","之后","关于","六","整个","心","性质","受到","政府","至","到了","作品","青年","目的","工人","规律","农民","元","变","实行","力量","非","一起","先生","后来","名","请","然后","干","办法","站","并不","制度","钱","有人","心理","怎样","原则","多少","处","原来","那个","等等","商品","干部","部","实践","您","所谓","低","行为","第","统一","拿","日本","矛盾","以上","大量","死","个人","指出","然而","代表","学校","原因","几个","达到","因素","感到","实验","地位","方向","正在","因而","程度","并且","完成","造成","八","回来","改变","往往","看见","政策","目前","半"]
            self.seed_punc = "，，，，，，，、、；；。。。。——！？"

        def lorem_zh(self,text):
            
            output=text.split(" ")
            i=0
            I=random.randint(1,15)
            for j,s in enumerate(output):
                if not re.search(r'xx\d\d',s):
                    output[j]=random.choice(self.seed)
                    i=i+1
                if i>=I:
                    output[j]=output[j]+random.choice(self.seed_punc)
                    i=0
                    I=random.randint(1,10)
            
            if not re.search('。',output[-1]):
                output[-1]=output[-1]+"。"

            # print(output)
            return "".join(output)
        
        def trans_text(self,text):
            return self.lorem_zh(text)
    
    return lorem_client()

def translator(client, text):
    # word_len=len(text.split())
    # zh_len=word_len*1.2
    return client,client.lorem_zh(text)
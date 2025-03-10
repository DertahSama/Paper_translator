import sys
# from transformers import AutoTokenizer
from time import sleep


def create_client():
    print('[**] 数数总共有多少字符和token')
    class clientclass():
        def __init__(self):
            self.translator_name='count_num'
            self.charnum=0
            self.tokennum=0
            # self.tnzer=AutoTokenizer.from_pretrained("./translators")


        def trans_text(self,text):
            self.charnum += len(text.replace(" ",""))
            # self.tokennum += len(self.tnzer.tokenize(text))
            return text


    client=clientclass()
    return client

# def translator(client,text):
#     client.count_and_add(text.replace(" ",""))
#     return client,text

if __name__=="__main__":
    client=create_client()
    en=r" Also shown in Fig. 3 are two additional cases that compare the variation of the shape at the two different elongations. The first case has the high elongation ( $\kappa=3$ ) of the TCV dee shape, but with higher triangularity ( $\delta=0.6$ ) and no squareness $(\lambda=0)$. Bessel functions is in the notation of G. N. Watson (1922). $a = 3\mathrm{m}^{-3}, b=16\mathrm{Wb}$.  "
    zh=client.trans_text(en)
    print([client.charnum,client.tokennum])
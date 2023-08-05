# !_*_ conding:utf-8 _*_
# __author__:QiongJJ
f = open("finance.txt","r",encoding = "utf-8")
data = f.readlines()

for name in data:#修改原始jieba词典库
    jieba.add_word(name.strip('\n') )
f.close()

def cut_for_search(str,hmm = True):
    seg_list = jieba.cut_for_search(str,HMM = hmm)
    print(" /".join(seg_list))

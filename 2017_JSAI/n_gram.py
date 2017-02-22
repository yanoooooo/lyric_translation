#coding:utf-8
# 指定したn-gramのファイルを作成
import nltk
import re

def create_bigram(filename, output):
    file = open(filename)
    data = file.read()
    file.close()
    data = data.replace("\n{2,}", "\n")
    data = data.replace("\n", " ")
    data = data.replace(",", "")
    data = data.replace(" {2,}", " ")
    tokens = data.split(" ")
    bigrams = nltk.bigrams(tokens)
    #fd = nltk.FreqDist(bigrams)
    dic = {}
    head_word = {}
    for a in bigrams:
        # トリミングのために不必要と考えられる文字
        trim = "；|：|、|。|「|」|【|】|（|）|？|！|・|　|ー|／|→|『|』|，|．|,|＞|＜|＊|●|■|＼|［|］|〔|〕|※|〈|〉|》|《"
        trim = trim + "|#|…|:|;|<|>|/|\n|@|{|}|~|=|%|§"
        trim = trim + "|[0-9]|[a-zA-Z]"
        trim = trim + "|\[|\]|\+|\*|\"|\&|\(|\)|\.|\!|\?|\-|\\\|\$|”|“|`"

        if not a[0]:
            continue
        
        if not re.match(trim, a[0]) and not re.match(trim, a[1]):
            bigram = a[0].strip()+","+a[1].strip()
            dic[bigram] = dic.get(bigram, 0) + 1
            head_word[a[0]] = head_word.get(a[0], 0) + 1
            #file.write(a[0]+","+a[1]+"\n")
            print("%s %s") % (a[0].decode("utf-8"), a[1].decode("utf-8"))
    file = open(output, "w")
    for k,v in dic.items():
        # bigramと出現頻度の書き出し
        # 単語の頻出度を確率とする
        word = k.split(",")
        if word[0] in head_word:
            #print word[0], head_word[word[0]]
            p = float(v) / float(head_word[word[0]])
            print "%s: %f" % (k, p)
            file.write(k+","+str(p)+"\n")
    file.close()


if __name__ == '__main__':
    test = ['datas/test/corpus.txt', 'datas/test/bigram.txt']
    piapro = ['datas/piapro/corpus.txt', 'datas/piapro/bigram.txt']
    translate = ['datas/translate/corpus.txt', 'datas/translate/bigram.txt']
    wiki = ['datas/wiki/corpus.txt', 'datas/wiki/bigram.txt']

    datas = wiki
    create_bigram(datas[0], datas[1])
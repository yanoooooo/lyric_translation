#coding:utf-8
#与えられたキーワードから文章を生成し、要約するプログラム

#http://tech.mof-mof.co.jp/blog/scikit-learn.html

import MeCab
from sklearn import svm

def extract_keyword(s):
    words = []
    result = []
    mt = MeCab.Tagger("-Ochasen")
    res = mt.parseToNode(s)
    while res:
        if res.surface:
            words.append(res.surface)
        ft = res.feature.split(",")
        if ft[0] == "名詞" or ft[0] == "動詞" or ft[0] == "形容詞":
            #print res.surface, ft[0]
            print res.surface, res.feature
            result.append(res.surface)
        res = res.next
    return result

if __name__ == '__main__':
    #s = "旅客の安全検査を一部簡素化する方向で検討する。"
    s = [
        ("私は知る必要がある", "I need to know", 4),
        ("人間の魂を持つ悪魔の性質", "the nature of the demons that possess man's soul!", 11),
        ("下を見て、あなたの足元の乞食を見なさい", "Look down and see the beggars at your feet", 10),
        ("あなたができるならば、見下ろして、ある程度の慈悲を示してください","Look down and show some mercy if you can", 10),
        ("ロンドン橋が落ちる", "London Bridge is falling down", 7),
        ("落ちる、落ちる", "Falling down, falling down", 6),
        ("ロンドン橋が落ちる", "London Bridge is falling down", 7),
        ("マイ ・ フェア ・ レディ", "My fair lady", 4)
    ]

    # キーワード抽出
    for i in range(len(s)):
        keywords = extract_keyword(s[i][0])
        print ",".join(keywords)

#coding:utf-8

import MeCab

"""
# 与えられた漢字混じりの文章をカタカナにして返す
@return string
"""
def kanji2katakana(sentence):
    #sentence = sentence.encode('utf-8')
    # 漢字をの読みを取得
    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    res = mt.parseToNode(sentence)
    
    result = ""

    while res:
        ft = res.feature.split(",")
        # もともとカタカナだった場合は*が入ってる
        if not ft[-2] == "*":
            result = result+ft[-2]
        else:
            result = result+res.surface
        res = res.next

    result = result.replace("*", "")
    return result

"""
# 与えられたカタカナの文章のモーラ数と、モーラ毎に区切ったリストを返す
# 促音や撥音の処理もここで
@return int, arr[]
"""
def count(sentence):
    lst = ["ッ", "ャ", "ュ", "ョ", "ン", "ァ", "ィ", "ゥ", "ェ", "ォ"]
    result = len(sentence)/3
    t = unicode(sentence.decode('utf-8'))

    # モーラ数を数える
    for num in range(0, len(t)):
        for a in lst:
            if a in t[num].encode("utf-8"):
                result = result - 1

    return result

# @param mora_src_obj [(mora_num, "lyrics", "翻訳"), (mora_num, "lyrics", "翻訳").....]
def count_mora(mora_src_obj):
    result = []

    for a in mora_src_obj:
        katakana = kanji2katakana(a[2])
        obj_mora = count(katakana)
        result.append((a[0], a[1], a[2], obj_mora))

    return result


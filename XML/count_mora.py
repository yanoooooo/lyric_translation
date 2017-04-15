#coding:utf-8

import MeCab

"""
# 与えられた漢字混じりの文章をカタカナにして返す
# 助詞が連続するなどの文章としておかしなものはここで弾く
@return string or false
"""
def kanji2katakana(sentence, particle=False):
    # 漢字をの読みを取得
    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    res = mt.parseToNode(sentence)
    
    result = ""
    old_part = ""

    while res:
        ft = res.feature.split(",")
        # 助詞が連続していないことが前提
        if particle == True:
            if not (old_part == "助詞" and ft[0] == "助詞"):
                # もともとカタカナだった場合は*が入ってる
                if not ft[-2] == "*":
                    result = result+ft[-2]
                else:
                    result = result+res.surface
            else:
                return False
        else:
            # もともとカタカナだった場合は*が入ってる
            if not ft[-2] == "*":
                result = result+ft[-2]
            else:
                result = result+res.surface
        #print res.surface, res.feature
        old_part = ft[0]
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

"""
# 与えられたカタカナの文章のモーラ数と、モーラ毎に区切ったリストを返す
# 促音や撥音の処理もここで
@return int, arr[]
"""
def count_mora_create_list(sentence):
    lst = ["ッ", "ャ", "ュ", "ョ", "ン", "ァ", "ィ", "ゥ", "ェ", "ォ"]
    result = len(sentence)/3
    mora_list = []
    t = unicode(sentence.decode('utf-8'))

    # モーラ数を数える
    for num in range(0, len(t)):
        for a in lst:
            if a in t[num].encode("utf-8"):
                result = result - 1

    mora_num = 0
    # モーラリストを作る
    for a in range(0, len(t)):
        if t[a].encode("utf-8") in lst:
            mora_list[mora_num-1] = mora_list[mora_num-1]+t[a]
        else:
            mora_list.append(t[a])
            mora_num = mora_num + 1

    #print sentence, result

    return result, mora_list

# @param sentence str
def kanji_count_mora(sentence):
    katakana = kanji2katakana(sentence)
    result = count(katakana)

    return result


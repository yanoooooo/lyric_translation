#coding:utf-8

import MeCab
import language_processing as lp

lst = ["ッ", "ャ", "ュ", "ョ", "ン", "ァ", "ィ", "ゥ", "ェ", "ォ"]

"""
# 与えられたカタカナの文章のモーラ数を返す
# 促音や撥音の処理もここで
@return int, arr[]
"""
def count_mora(sentence):
    result = len(sentence)/3
    t = unicode(sentence.decode('utf-8'))

    # モーラ数を数える
    for num in range(0, len(t)):
        for a in lst:
            if a in t[num].encode("utf-8"):
                result = result - 1

    return result

"""
# 与えられたカタカナの文章をモーラ毎に区切ったリストを返す
# 促音や撥音の処理もここで
@return arr[]
"""
def create_mora_list(sentence):
    result = []
    t = unicode(sentence.decode('utf-8'))

    mora_num = 0
    # モーラリストを作る
    for a in range(0, len(t)):
        if t[a].encode("utf-8") in lst:
            result[mora_num-1] = result[mora_num-1]+t[a]
        else:
            result.append(t[a])
            mora_num = mora_num + 1

    #print sentence, result

    return result

# @param sentence str
def kanji_count_mora(sentence):
    katakana = lp.kanji2katakana(sentence)
    result = count_mora(katakana)

    return result


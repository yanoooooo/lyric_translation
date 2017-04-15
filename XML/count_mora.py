#coding:utf-8

import MeCab
import language_processing as lp

lst = ["ッ", "ャ", "ュ", "ョ", "ン", "ァ", "ィ", "ゥ", "ェ", "ォ"]

"""
# 与えられたカタカナの文章のモーラ数と、モーラ毎に区切ったリストを返す
# 促音や撥音の処理もここで
@return int, arr[]
"""
def count(sentence):
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
    katakana = lp.kanji2katakana(sentence)
    result = count(katakana)

    return result


#coding:utf-8
# XMLを読み込み歌詞とモーラ数を取り出す
# 前提条件として、歌詞はピリオドで区切る
import sys
from xml.etree.ElementTree import *

"""
# MusicXMLからモーラ数と原言語を抽出
@param filename
@return array [(mora_num, "lyrics"), (mora_num, "lyrics").....]
"""
def __parse_xml(filename):
    result = []
    tree = parse(filename)
    elem = tree.getroot()

    mora = 0
    lyrics = ""
    for e in elem.findall(".//lyric"):
        text = e.find(".//text").text
        syllabic = e.find(".//syllabic").text

        if syllabic == "single" or syllabic == "begin":
            lyrics = lyrics + " " + text
        else:
            lyrics = lyrics + text
        mora = mora + 1

        # ピリオドやカンマ等でフレーズを切る
        if "." in text or "," in text or ";" in text:
            result.append((mora, lyrics.strip()))
            mora = 0
            lyrics = ""
    #for a  in result:
    #    print a[0], a[1]

    return result

def read_xml():
    argvs = sys.argv
    if len(argvs) != 2:
        print "Usage: input MusicXML file name"
        quit()

    # MusicXML file
    filename = argvs[1]

    # [(mora_num, "lyrics"), (mora_num, "lyrics").....]
    result = __parse_xml(filename)
    
    return result

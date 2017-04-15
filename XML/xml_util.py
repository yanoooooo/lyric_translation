#coding:utf-8
# XMLを読み込み歌詞とモーラ数を取り出す
# 前提条件として、歌詞はピリオドで区切る
import sys
from xml.etree.ElementTree import *
import jaconv
import count_mora as cm
import language_processing as lp

notes = {"quarter":4, "eighth":8}

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

"""
# 渡されたフレーズを解析し、歌詞に伸ばしを入れる
"""
def __less_mora(score, lyrics):
    result = ""
    not_type = []

    for s in score:
        not_type.append(notes[s.find(".//type").text])
        #print s.find(".//type").text

    # オリジナルと訳詞の差分モーラ
    diff_mora = len(not_type) - len(lyrics)
    mora = 0
    # 配列から１番短い音の次の音を伸ばし棒にする
    # TODO 愚直に最初に当たったやつからやってる
    while diff_mora > 0:
        # 次の音の方が短ければ、伸ばす
        for num in range(0, len(not_type)-1):
            if not_type[num] > not_type[num+1]:
                #print lyrics[:num+1], lyrics[num+1:]
                lyrics = lyrics[:num+1] + u"ー" + lyrics[num+1:]
                diff_mora = diff_mora - 1
            if diff_mora == 0:
                break

    result = lyrics
    return result

"""
# 渡された歌詞とモーラ数からxmlを作成する
@param lyrics arr[(lyrics_mora, "lyrics"), (lyrics_mora, "lyrics")...]
"""
def create_xml(lyrics, output):
    argvs = sys.argv
    if len(argvs) != 2:
        print "Usage: input MusicXML file name"
        quit()

    # MusicXML fil
    filename = argvs[1]

    # もとの歌詞とモーラ数の取得
    org_lyrics = read_xml()

    # xmlファイルデータの取得
    tree = parse(filename)
    elem = tree.getroot()

    # オリジナルと訳詞の配列のフレーズ数が同じであること前提
    sum_mora = 0
    org_sum_mora = 0
    for num in range(0, len(lyrics)):
        mora = lyrics[num][0]
        katakana = unicode(lp.kanji2katakana(lyrics[num][1]).decode("utf-8"))
        # TODO 撥音などがあるので、リストで取得しないとだめだ！！！！！！！！！！！！！
        # count_mora_create_listを使う必要がある！！！！！！！！！
        # カタカナは読みにくいので平仮名にしてあげる
        hiragana = jaconv.kata2hira(katakana)
        #print katakana, type(katakana), len(katakana), mora
        
        # オリジナルと翻訳のモーラ数が同じ
        if org_lyrics[num][0] == mora:
            for n in range(0, mora):
                elem.findall(".//lyric")[sum_mora+n].find(".//text").text = hiragana[n]
            sum_mora = sum_mora + mora
            print "same"

        # オリジナルより翻訳のモーラ数が少ない
        if org_lyrics[num][0] > mora:
            # 該当するスコア部分の切り出し / lyricsを含むnoteを切り出す
            # オリジナルスコアのモーラ数とフレーズの部分を切りだす
            score = elem.findall(".//lyric/..")[org_sum_mora:org_sum_mora+org_lyrics[num][0]]
            # オリジナルのモーラ数に歌詞数をあわせる
            hiragana = __less_mora(score, hiragana)
            #print hiragana

            # 要素の入れ替え
            for n in range(0, org_lyrics[num][0]):
                #print hiragana[n]
                elem.findall(".//lyric")[sum_mora+n].find(".//text").text = hiragana[n]
                #print elem.findall(".//lyric")[n].find(".//text").text
            sum_mora = sum_mora + org_lyrics[num][0]
            print "less"

        # オリジナルより翻訳のモーラ数が多い
        if org_lyrics[num][0] < mora:
            print "more"

        
        org_sum_mora = org_sum_mora + org_lyrics[num][0]

    # xmlの書き出し
    tree = ElementTree(elem)
    tree.write(output)

    for a in lyrics:
        print a[0], a[1]

    for b in org_lyrics:
       print b[0], b[1]
    print "Done!"


if __name__ == '__main__':
    lyrics = [(7, "栗木の下で"), (7, "あなたと私"), (8, "幸せはでそう"), (7, "栗木の下で")]
    create_xml(lyrics, "./test.xml")
#coding:utf-8
# XMLを読み込み歌詞とモーラ数を取り出す
# 前提条件として、歌詞はピリオドで区切る
import sys
import copy
from xml.etree.ElementTree import *
import jaconv
import count_mora as cm
import language_processing as lp

notes = {"half":2, "quarter":4, "eighth":8, "16th": 16}

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
# オリジナルよりモーラ数が少ない場合、渡されたフレーズを解析し、歌詞に伸ばしを入れる
@param score element
@param mora_list arr["ロン", "ドン"....]
return arr mora_list
"""
def __less_mora(score, mora_list):
    result = mora_list[:]
    note_type = []

    for s in score:
        note_type.append(notes[s.find(".//type").text])
        #print s.find(".//type").text
    
    # オリジナルと訳詞の差分モーラ
    diff_mora = len(note_type) - len(result)
    # 配列から１番短い音の次の音を伸ばし棒にする
    # TODO 愚直に最初に当たったやつからやってるのでもうちょっと音符考慮して…
    # TODO 符点が考慮できてない</dot>というタグがつく
    while diff_mora > 0:
        # 次の音の方が短ければ、伸ばす
        for num in range(0, len(note_type)-1):
            if note_type[num] > note_type[num+1]:
                result.insert(num, u"ー")
                #lyrics = lyrics[:num+1] + u"ー" + lyrics[num+1:]
                diff_mora = diff_mora - 1
            if diff_mora == 0:
                break
        # 全部の音が等価だった、もしくは短い音符が少なかった場合
        # 最後に伸ばしをつけることで一旦回避
        if diff_mora > 0:
            for num in range(0, diff_mora):
                result.append(u"ー")
                diff_mora = diff_mora - 1
            break

    return result

"""
# オリジナルよりモーラ数が多い場合、音符を増やす
@param score element.part.measure
@param mora_list arr["ロン", "ドン"....]
return score
"""
def __more_mora(measure, mora_list):
    result = measure[:]
    note_type = []

    # 小節ごとの音符を取得する
    # arr[[2,4,4], [4,4,4,4]....]
    for ms in measure:
        types = []
        for note in ms.iter("note"):
            for t in note.iter("type"):
                types.append(notes[t.text])
                #print t.text
        note_type.append(types)
    
    # オリジナルと訳詞の差分モーラ
    sum_mora = 0
    for nt in note_type:
        sum_mora = sum_mora + len(nt)
    diff_mora = len(mora_list) - sum_mora
    
    # 配列内で１番大きい音符を分割していく
    # TODO 符点を考慮していない
    # TODO 先頭から愚直に分割している
    while diff_mora > 0:
        # 繰り返して最小の値を探す
        for ms_num in range(0, len(result)):
            mn = min(note_type[ms_num])
            score = result[ms_num].findall("note")
            for num in range(0, len(score)):
                #print score[num].find(".//type").text
                if score[num].find(".//type").text == notes.keys()[notes.values().index(mn)]:
                    # 音符を挿入
                    node = copy.deepcopy(score[num])
                    result[ms_num].insert(num, node)
                    # 音長を変更
                    # TODO notesに値が無い場合はエラーで落ちる
                    result[ms_num][num].find(".//type").text = notes.keys()[notes.values().index(mn*2)]
                    result[ms_num][num+1].find(".//type").text = notes.keys()[notes.values().index(mn*2)]
                    diff_mora = diff_mora - 1
                if diff_mora == 0:
                    break
            # note_typeの更新
            note_type = []
            for ms in measure:
                types = []
                for note in ms.iter("note"):
                    for t in note.iter("type"):
                        types.append(notes[t.text])
                        #print t.text
                note_type.append(types)
            

    #for s in result:
    #    print s.find(".//type").text
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
    current_mora = 0
    #org_sum_mora = 0
    for num in range(0, len(lyrics)):
        #katakana = unicode(lp.kanji2katakana(lyrics[num][1]).decode("utf-8"))
        katakana = lp.kanji2katakana(lyrics[num][1])
        mora_list = cm.create_mora_list(katakana)

        # ----------------オリジナルと翻訳のモーラ数が同じ----------------
        if org_lyrics[num][0] == lyrics[num][0]:
            # 要素の入れ替え
            for n in range(0, lyrics[num][0]):
                #print jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//text").text = jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//syllabic").text = "single"
            current_mora = current_mora + lyrics[num][0]
            #print "same"

        # ----------------オリジナルより翻訳のモーラ数が少ない----------------
        if org_lyrics[num][0] > lyrics[num][0]:
            # 該当するスコア部分の切り出し / lyricsを含むnoteを切り出す
            # オリジナルスコアのモーラ数とフレーズの部分を切りだす
            score = elem.findall(".//lyric/..")[current_mora:current_mora+org_lyrics[num][0]]
            # オリジナルのモーラ数に歌詞数をあわせる
            mora_list = __less_mora(score, mora_list)

            # 要素の入れ替え
            for n in range(0, org_lyrics[num][0]):
                elem.findall(".//lyric")[current_mora+n].find(".//text").text = jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//syllabic").text = "single"
                #print elem.findall(".//lyric")[n].find(".//text").text
            current_mora = current_mora + org_lyrics[num][0]
            #print "less"

        # ----------------オリジナルより翻訳のモーラ数が多い----------------
        if org_lyrics[num][0] < lyrics[num][0]:
            # 該当するスコア部分の切り出し / lyricsを含むnoteを切り出す
            # オリジナルスコアのモーラ数とフレーズの部分を切りだす
            score = elem.findall(".//lyric/..")[current_mora:current_mora+org_lyrics[num][0]]

            # 変更箇所は小節ごと切り出す
            modify_measure = []
            for measure in elem.findall(".//measure"):
                for note in measure.findall("note"):
                    if note in score and not (measure in modify_measure):
                        modify_measure.append(measure)

            # 小節ごと渡して、音符を編集
            new_elem = __more_mora(modify_measure, mora_list)

            # 切り出した小節を新しいものと入れ替え
            elem_num = 0
            measure_num = 0
            for part in elem.findall("part"):
                for measure in elem.findall("measure"):
                    if measure in new_elem:
                        part.remove(measure)
                        part.insert(measure_num, new_elem[elem_num])
                        elem_num = elem_num + 1
                    measure_num = measure_num + 1

            # 要素の入れ替え
            for n in range(0, lyrics[num][0]):
                # print elem.findall(".//lyric")[current_mora+n].find(".//text").text
                elem.findall(".//lyric")[current_mora+n].find(".//text").text = jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//syllabic").text = "single"

            current_mora = current_mora + lyrics[num][0]
            print "more"

    # xmlの書き出し
    tree = ElementTree(elem)
    tree.write(output)

    for a in lyrics:
        print a[0], a[1]

    for b in org_lyrics:
       print b[0], b[1]
    print "Done!"


if __name__ == '__main__':
    #lyrics = [(7, "栗木の下で"), (7, "あなたと私"), (8, "幸せはでそう"), (7, "栗木の下で")]
    lyrics = [(7, "ロンドン橋落ちる"), (3, "落ちる"), (3, "落ちる"), (7, "ロンドン橋落ちる"), (6, "マイフェアレディ")]
    create_xml(lyrics, "./test.xml")
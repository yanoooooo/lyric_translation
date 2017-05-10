#coding:utf-8
# XMLを読み込み歌詞とモーラ数を取り出す
# 前提条件として、歌詞はピリオドで区切る
import sys
import copy
import xml.etree.ElementTree as ET
import jaconv
import count_mora as cm
import language_processing as lp

types = {"whole":1, "half":2, "quarter":4, "eighth":8, "16th": 16, "32nd": 32}
durations = {"whole":4, "half":4, "quarter":2, "eighth":1, "16th": 1, "32nd": 1}

"""
# MusicXMLからモーラ数と原言語を抽出
@param filename
@return array [(mora_num, "lyrics"), (mora_num, "lyrics").....]
"""
def __parse_xml(filename):
    result = []
    tree = ET.parse(filename)
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
    #print result, len(result) # 歌詞のモーラ数

    for s in score:
        note_type.append(types[s.find(".//type").text])
        #print s.find(".//step").text
    #print note_type, len(note_type) # 原語のモーラ数
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
# 曲の拍子と1小節の合計数を求める
@param elem
return time {"beat":0, "beat-type":0, "sum":0.0}
"""
def calc_note(elem):
    result = {"beat":0, "beat-type":0, "sum":0.0}
    time = elem.find(".//time")

    result["beat"] = float(time.find("beats").text)
    result["beat-type"] = float(time.find("beat-type").text)
    result["sum"] = (4/float(time.find("beat-type").text)) * float(time.find("beats").text)

    return result

"""
# オリジナルよりモーラ数が多い場合、音符を増やす
@param score element.part.measure
@param mora_list arr["ロン", "ドン"....]
return score
"""
def __more_mora(time, measure, mora_list, org_mora):
    result = measure[:]
    # この2つの配列は常に配列数が揃う
    note_type = []
    note_pitch = []
    node_lyric = ""

    # 小節ごとの音符を取得する
    # 符点を考慮する
    # arr[[(2.0, <pitch>), (1.0, <pitch>), (1.0, <pitch>)], [(1.5, <pitch>), (1.5, <pitch>), (1.0, <pitch>)]....]
    for ms in measure:
        tys = []
        pit = []
        n = 0.0
        for note in ms.iter("note"):
            for t in note.iter("type"):
                if note.find("dot") != None:
                    n = 4/float(types[t.text]) + (4/float(types[t.text]))/2
                else:
                    n = 4/float(types[t.text])
                #tys.append((n, note.find(".//pitch")))
                if node_lyric == "":
                    node_lyric = note.find(".//lyric")
                tys.append(n)
                pit.append(note.find(".//pitch"))
        note_type.append(tys)
        note_pitch.append(pit)
    #print note_type
    #print note_pitch
    
    # オリジナルと訳詞の差分モーラ
    #sum_mora = 0
    #for nt in note_type:
    #    sum_mora = sum_mora + len(nt)
    #diff_mora = len(mora_list) - sum_mora
    diff_mora = len(mora_list) - org_mora
    #print diff_mora

    # 最大値を分割し、差分が無くなるまで処理を繰り返す
    # アウフタクトはいじるべきではない
    upbeat = []
    upbeat_pitch = []
    #if sum([note[0] for note in note_type[0]]) != time["sum"]:
    if sum(note_type[0]) != time["sum"]:
        upbeat = note_type[0]
        upbeat_pitch = note_pitch[0]
        note_type.pop(0)
        note_pitch.pop(0)
    while diff_mora > 0:
        # 最大値を持つ1番先頭の配列とindexを得る
        measure = note_type[note_type.index(max(note_type))]
        index = note_type.index(max(note_type))
        measure_pitch = note_pitch[index]
        #print measure, note_type.index(max(note_type))
        # 最大値
        mx = max(measure)
        # 符点の場合は3で割れる
        if (mx*1000) % 3 == 0:
            # 2:1になるようにする
            for num in range(0, len(measure)):
                if measure[num] == mx:
                    measure_pitch.insert(num+1, measure_pitch[measure.index(mx)])
                    measure[num] = (mx/3)*2
                    measure.insert(num+1, mx/3)
                    diff_mora = diff_mora - 1
                    break
            note_type[index] = measure
            note_pitch[index] = measure_pitch
        # 符点でないとき
        else:
            # 半分に分割
            for num in range(0, len(measure)):
                if measure[num] == mx:
                    measure_pitch.insert(num+1, measure_pitch[measure.index(mx)])
                    measure[num] = mx/2
                    measure.insert(num+1, mx/2)
                    diff_mora = diff_mora - 1
                    break
            note_type[index] = measure
            note_pitch[index] = measure_pitch
    # アウフタクトを先頭に挿入
    if len(upbeat) > 0:
        note_type.insert(0, upbeat)
        note_pitch.insert(0, upbeat_pitch)
    #print note_type
    #print note_pitch

    # note_typeの数とelem:measure(result)の数が揃っている前提でxmlを編集
    for num in range(0, len(result)):
        #print len(result[num].findall("note")), len(note_type[num])
        # 小節内の音符数が違ったら増やす処理が必要
        diff_note = len(note_type[num]) - len(result[num].findall("note"))
        if diff_note > 0:
            score = result[num].findall("note")
            # noteを増やす
            for dn in range(0, diff_note):
                node = copy.deepcopy(score[0])
                result[num].insert(num, node)
            # noteの書き換え
            for note_num in range(0, len(note_type[num])):
                if result[num][note_num].find(".//type") != None:
                    #print note_pitch[num][note_num], result[num][note_num].find(".//step")
                    # note_pitchに音があるのに、resultに無いときはpitchを追加
                    if note_pitch[num][note_num] != None and result[num][note_num].find(".//step") == None:
                        # 歌詞の追加
                        result[num][note_num].append(copy.deepcopy(node_lyric))
                        # ピッチの追加
                        result[num][note_num].insert(note_num, copy.deepcopy(note_pitch[num][note_num]))
                        # 休符の削除
                        result[num][note_num].remove(result[num][note_num].find(".//rest"))
                    # note_pitchに音が無いのに、resultにあるときはpitchを削除
                    elif note_pitch[num][note_num] == None and result[num][note_num].find(".//step") != None:
                        #print result[num][note_num],result[num][note_num].find(".//step").text
                        # ピッチの削除
                        result[num][note_num].remove(result[num][note_num].find(".//pitch"))
                        # 歌詞の削除
                        result[num][note_num].remove(result[num][note_num].find(".//lyric"))
                        # restの追加
                        result[num][note_num].insert(0, ET.fromstring("<rest />"))
                    # どっちもピッチがあるとき
                    elif note_pitch[num][note_num] != None and result[num][note_num].find(".//step") != None:
                        result[num][note_num].find(".//step").text = note_pitch[num][note_num].find(".//step").text
                        result[num][note_num].find(".//octave").text = note_pitch[num][note_num].find(".//octave").text

                    result[num][note_num].find(".//type").text = types.keys()[types.values().index(4 / note_type[num][note_num])]
                    result[num][note_num].find(".//duration").text = str(durations[types.keys()[types.values().index(4 / note_type[num][note_num])]])
                # 符点ではない場合dotを削除
                if (note_type[num][note_num]*1000) % 3 != 0:
                    for n in result[num]:
                        for child in n:
                            if child == result[num][note_num].find("dot"):
                                n.remove(result[num][note_num].find("dot"))
                # TODO 符点の場合は符点を挿入
                    #print result.remove(rm)
                    #result[num][note_num].remove(".//dot")

    #for num in range(0, len(score)):
    #    print score[num]

    # 結果を返す
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
    tree = ET.parse(filename)
    elem = tree.getroot()

    # 1小節の音符数
    time = calc_note(elem)

    # オリジナルと訳詞の配列のフレーズ数が同じであること前提
    current_mora = 0
    #org_sum_mora = 0
    for num in range(0, len(lyrics)):
        #katakana = unicode(lp.kanji2katakana(lyrics[num][1]).decode("utf-8"))
        katakana = lp.kanji2katakana(lyrics[num][1])
        mora_list = cm.create_mora_list(katakana)

        # ----------------オリジナルと翻訳のモーラ数が同じ----------------
        if org_lyrics[num][0] == lyrics[num][0]:
            print "============ same =============="
            # 要素の入れ替え
            for n in range(0, lyrics[num][0]):
                #print n, mora_list[n]
                #print jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//text").text = jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//syllabic").text = "single"
            current_mora = current_mora + lyrics[num][0]

        # ----------------オリジナルより翻訳のモーラ数が少ない----------------
        if org_lyrics[num][0] > lyrics[num][0]:
            print "============ less =============="
            # 該当するスコア部分の切り出し / lyricsを含むnoteを切り出す
            # オリジナルスコアのモーラ数とフレーズの部分を切りだす
            score = elem.findall(".//lyric/..")[current_mora:current_mora+org_lyrics[num][0]]
            #print current_mora, current_mora+org_lyrics[num][0], len(score), len(elem.findall(".//lyric/.."))
            # オリジナルのモーラ数に歌詞数をあわせる
            mora_list = __less_mora(score, mora_list)

            # 要素の入れ替え
            for n in range(0, org_lyrics[num][0]):
                #print n, mora_list[n]
                elem.findall(".//lyric")[current_mora+n].find(".//text").text = jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//syllabic").text = "single"
                #print elem.findall(".//lyric")[n].find(".//text").text
            current_mora = current_mora + org_lyrics[num][0]

        # ----------------オリジナルより翻訳のモーラ数が多い----------------
        if org_lyrics[num][0] < lyrics[num][0]:
            print "============ more =============="
            # 該当するスコア部分の切り出し / lyricsを含むnoteを切り出す
            # オリジナルスコアのモーラ数とフレーズの部分を切りだす
            score = elem.findall(".//lyric/..")[current_mora:current_mora+org_lyrics[num][0]]
            #print current_mora, current_mora+org_lyrics[num][0], len(score), len(elem.findall(".//lyric/.."))
            # 変更箇所は小節ごと切り出す
            modify_measure = []
            for measure in elem.findall(".//measure"):
                for note in measure.findall("note"):
                    if note in score and not (measure in modify_measure):
                        modify_measure.append(measure)
            # 小節ごと渡して、音符を編集
            #print modify_measure
            new_elem = __more_mora(time, modify_measure, mora_list, org_lyrics[num][0])

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
                #print n, mora_list[n]
                #print current_mora+n, elem.findall(".//lyric")[current_mora+n].find(".//text").text, jaconv.kata2hira(mora_list[n]), elem.findall(".//pitch")[current_mora+n].find(".//step").text
                elem.findall(".//lyric")[current_mora+n].find(".//text").text = jaconv.kata2hira(mora_list[n])
                elem.findall(".//lyric")[current_mora+n].find(".//syllabic").text = "single"

            current_mora = current_mora + lyrics[num][0]

    # xmlの書き出し
    tree = ET.ElementTree(elem)
    tree.write(output)

    for a in lyrics:
        print a[0], a[1]

    for b in org_lyrics:
       print b[0], b[1]
    print "Done!"


if __name__ == '__main__':
    #lyrics = [(7, "栗木の下で"), (7, "あなたと私"), (8, "幸せはでそう"), (7, "栗木の下で")]
    lyrics = [(7, "ロンドン橋落ちる"), (3, "落ちる"), (3, "落ちる"), (7, "ロンドン橋落ちる"), (6, "マイフェアレディ")]
    #lyrics = [(16, "スパイダー水注ぎ口上がった"), (10, "洗い流されれれれ"), (14, "太陽出て乾燥し雨中"), (13, "スパイダー再び口行った")]
    #lyrics = [(25, "どのよう甘い響き私ようなそは救われました"), (4, "失わ"), (2, "発見"), (4, "盲目")]
    create_xml(lyrics, "./test.xml")
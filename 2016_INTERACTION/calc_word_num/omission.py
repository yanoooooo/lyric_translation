#coding:utf-8
# 読み込んだファイルの格助詞を抜いた時の歌詞の一致率を求める
# difflibを使う

import MeCab
import difflib
import jaconv

filename = "data.csv"

file = open("data/"+filename)
lines = file.readlines()
file.close()

# 形態素解析
def non_processing(res):
    l = ""
    while res:
        if res.surface:
            ft = res.feature.split(",")
            #if ft[1] != "格助詞" and res.surface != "私":
            #if ft[1] != "格助詞":
            if len(ft) > 7:
                l = l+jaconv.kata2hira(ft[7].decode('utf-8')).encode('utf-8')
            else:
                l = l+jaconv.kata2hira(res.surface.decode('utf-8')).encode('utf-8')
        res = res.next
    return l

def delete_jyoshi(res):
    l = ""
    while res:
        if res.surface:
            ft = res.feature.split(",")
            if ft[1] != "格助詞":
                if len(ft) > 7:
                    l = l+jaconv.kata2hira(ft[7].decode('utf-8')).encode('utf-8')
                else:
                    l = l+jaconv.kata2hira(res.surface.decode('utf-8')).encode('utf-8')
        res = res.next
    return l

def delete_watashi(res):
    l = ""
    while res:
        if res.surface:
            ft = res.feature.split(",")
            #if ft[1] != "格助詞" and res.surface != "私":
            if res.surface != "私":
                if len(ft) > 7:
                    l = l+jaconv.kata2hira(ft[7].decode('utf-8')).encode('utf-8')
                else:
                    l = l+jaconv.kata2hira(res.surface.decode('utf-8')).encode('utf-8')
        res = res.next
    return l

def delete_both(res):
    l = ""
    while res:
        if res.surface:
            ft = res.feature.split(",")
            if ft[1] != "格助詞" and res.surface != "私":
                if len(ft) > 7:
                    l = l+jaconv.kata2hira(ft[7].decode('utf-8')).encode('utf-8')
                else:
                    l = l+jaconv.kata2hira(res.surface.decode('utf-8')).encode('utf-8')
        res = res.next
    return l


if __name__ == '__main__':
    diff = 0.0
    line_sum = 0
    tunes = 0
    source = "google"
    for line in lines:
        if line == "\n":
            tunes = tunes+1
            continue
        mt = MeCab.Tagger("-Ochasen")
        # bing, google, ひらがな, 漢字
        lyrics = line.split(",")
        if source == "bing":
            res = mt.parseToNode(lyrics[0])
        else:
            res = mt.parseToNode(lyrics[1])

        # 加工していない直訳と正解の比較
        #l = non_processing(res)

        # 助詞を抜いた直訳と正解の比較
        #l = delete_jyoshi(res)

        # 一人称「私」を抜いた直訳と正解の比較
        #l = delete_watashi(res)

        # 両方消した結果
        l = delete_both(res)

        # 表記ゆれとなるので句読点などを消す
        l = l.replace("*", "")
        l = l.replace("、", "")
        l = l.replace("!", "")
        l = l.replace("?", "")
        l = l.replace("・", "")
        l = l.replace("。", "")
        s = difflib.SequenceMatcher(None, l.strip(), lyrics[2].strip()).ratio()
        #print line
        if s > 0.65:
            print l, "<~>", lyrics[2].strip()
            print "match ratio:", s, "\n"
        diff = diff+s
        line_sum = line_sum+1

    print u"曲数 %s" % (tunes+1)
    print u"差分率の合計:%s, フレーズ数:%s" % (diff, line_sum)
    print u"差分率:%s" % (diff/float(line_sum))




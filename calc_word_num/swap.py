#coding:utf-8
# 読み込んだファイルの行前後にその行の単語が含まれている確立を調べる

import MeCab

filename = "data.csv"

file = open("data/"+filename)
lines = file.readlines()
file.close()

# 次のフレーズに単語が含まれる確率
def after_swap(source):
    corr_sum = 0
    word_inc = 0
    tunes = 0
    flg = 0
    phrase_sum = 0
    array = list(lines)
    for i in range(len(array)-1):
        flg = 0
        if array[i] == "\n":
            tunes = tunes+1
        if array[i] == "\n" or array[i+1] == "\n":
            continue
        mt = MeCab.Tagger("-Ochasen")
        lyrics = array[i].split(",")
        next_line = array[i+1].split(",")
        # 正解文の合計を求める
        corr_sum = corr_sum + sum_word(next_line[3])
        # bing, google, ひらがな, 漢字
        res = mt.parseToNode(next_line[3])
        while res:
            if res.surface:
                ft = res.feature.split(",")
                #print res.surface, ft[0]
                if ft[0] == "名詞" or ft[0] == "動詞" or ft[0] == "形容詞" or ft[0] == "副詞":
                    mt2 = MeCab.Tagger("-Ochasen")
                    if source == "bing":
                        res2 = mt2.parseToNode(lyrics[0])
                    else:
                        res2 = mt2.parseToNode(lyrics[1])
                    while res2:
                        if res2.surface == "\n":
                            continue
                        ft2 = res2.feature.split(",")
                        #if res.surface == res2.surface:
                        if ft[6] == ft2[6]:
                            word_inc = word_inc+1
                            flg = 1
                            #print res.surface, res2.surface
                            #print next_line[3], lyrics[1]
                            break
                        res2 = res2.next
            res = res.next
        if flg == 1:
            phrase_sum = phrase_sum+1
    
    print "単語含有率:%s" % (float(word_inc) / float(corr_sum))
    print "一致単語数: %s, 正解文単語数: %s\n" % (word_inc, corr_sum)
    print "フレーズ含有率:%s" % (float(phrase_sum) / float(len(lines)-tunes))
    print "フレーズ一致数: %s, 全フレーズ数: %s\n" % (phrase_sum, len(lines)-tunes)
    print u"曲数 %s" % (tunes+1)

# 前のフレーズに単語が含まれる確率
def before_swap(source):
    corr_sum = 0
    word_inc = 0
    tunes = 0
    flg = 0
    phrase_sum = 0
    array = list(lines)
    for i in reversed(xrange(len(array))):
        flg = 0
        if array[i] == "\n":
            tunes = tunes+1
        if array[i] == "\n" or array[i-1] == "\n":
            continue
        mt = MeCab.Tagger("-Ochasen")
        lyrics = array[i].split(",")
        next_line = array[i-1].split(",")
        # 正解文の合計を求める
        corr_sum = corr_sum + sum_word(next_line[3])
        # bing, google, ひらがな, 漢字
        res = mt.parseToNode(next_line[3])
        while res:
            if res.surface and i != 0:
                ft = res.feature.split(",")
                if ft[0] == "名詞" or ft[0] == "動詞" or ft[0] == "形容詞" or ft[0] == "副詞":
                    mt2 = MeCab.Tagger("-Ochasen")
                    if source == "bing":
                        res2 = mt2.parseToNode(lyrics[0])
                    else:
                        res2 = mt2.parseToNode(lyrics[1])
                    while res2:
                        if res2.surface == "\n":
                            continue
                        ft2 = res2.feature.split(",")
                        #if res.surface == res2.surface:
                        if ft[6] == ft2[6]:
                            word_inc = word_inc+1
                            flg = 1
                            #print res.surface, res2.surface
                            #print next_line[3], lyrics[1]
                            break
                        res2 = res2.next
            res = res.next

        if flg == 1:
            phrase_sum = phrase_sum+1

    print "単語含有率:%s" % (float(word_inc) / float(corr_sum))
    print "一致単語数: %s, 正解文単語数: %s\n" % (word_inc, corr_sum)
    print "フレーズ含有率:%s" % (float(phrase_sum) / float(len(lines)-tunes))
    print "フレーズ一致数: %s, 全フレーズ数: %s\n" % (phrase_sum, len(lines)-tunes)
    print u"曲数 %s" % (tunes+1)

# 同じフレーズに単語が含まれる確率
def same_swap(source):
    corr_sum = 0
    word_inc = 0
    tunes = 0
    flg = 0
    phrase_sum = 0
    array = list(lines)
    for i in range(len(array)):
        flg = 0
        if array[i] == "\n":
            tunes = tunes+1
            continue
        mt = MeCab.Tagger("-Ochasen")
        lyrics = array[i].split(",")
        # 正解文の合計を求める
        corr_sum = corr_sum + sum_word(lyrics[3])
        # bing, google, ひらがな, 漢字
        res = mt.parseToNode(lyrics[3])
        while res:
            if res.surface:
                ft = res.feature.split(",")
                if ft[0] == "名詞" or ft[0] == "動詞" or ft[0] == "形容詞" or ft[0] == "副詞":
                    mt2 = MeCab.Tagger("-Ochasen")
                    if source == "bing":
                        res2 = mt2.parseToNode(lyrics[0])
                    else:
                        res2 = mt2.parseToNode(lyrics[1])
                    #print res.surface
                    while res2:
                        if res2.surface == "\n":
                            continue
                        ft2 = res2.feature.split(",")
                        #if res.surface == res2.surface:
                        if ft[6] == ft2[6]:
                            #print res.surface, ft[6]
                            word_inc = word_inc+1
                            flg = 1
                            #print res.surface, res2.surface
                            #print lyrics[3], lyrics[1]
                            break
                        res2 = res2.next
            res = res.next
        if flg == 1:
                phrase_sum = phrase_sum+1

    #print "包括率:%s\n" % (float(word_inc) / float(word_sum))
    print "単語含有率:%s" % (float(word_inc) / float(corr_sum))
    print "一致単語数: %s, 正解文単語数: %s\n" % (word_inc, corr_sum)
    print "フレーズ含有率:%s" % (float(phrase_sum) / float(len(lines)-tunes))
    print "フレーズ一致数: %s, 全フレーズ数: %s\n" % (phrase_sum, len(lines)-tunes)
    print u"曲数 %s" % (tunes+1)

def sum_word(line):
    result = 0
    mt = MeCab.Tagger("-Ochasen")
    res = mt.parseToNode(line)
    while res:
        if res.surface:
            ft = res.feature.split(",")
            if ft[0] == "名詞" or ft[0] == "動詞" or ft[0] == "形容詞" or ft[0] == "副詞":
                result = result+1
        res = res.next
    return result

if __name__ == '__main__':
    source = "google" #0:bing, 1:google
    print "============= 前のフレーズに含まれる ============="
    before_swap(source)
    
    print "============= 次のフレーズに含まれる ============="
    after_swap(source)

    print "============= 同じフレーズに含まれる ============="
    same_swap(source)

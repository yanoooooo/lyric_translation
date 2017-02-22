#coding:utf-8
#機械翻訳文から歌詞を生成する

import nltk
import MeCab
import jaconv
import re
from gensim.models import word2vec

"""
# ファイルからbigramを読み込んでそのリストを返す
@return array[tuple(word1, word2, freq), tuple...]
"""
def create_bigram(filename):
    bigrams = []

    # (word1, word2, frequency)
    for row in open(filename).readlines():
        row = row.strip().split(',')
        bigrams.append(tuple(row))
    print "DONE...%d objects created" % len(bigrams)
    return bigrams

"""
# 与えられた単語と前方が一致するbigramのリストを返す
@return array[tuple(word1, word2, sentence, freq), tuple...]
"""
def search_bigram(bigrams, word):
    result = []
    for a in bigrams:
        if a[0] == word:
            result.append((a[0], a[1], a[0]+a[1], a[2]))
    return result

"""
# 与えられた漢字混じりの文章をカタカナにして返す
# 助詞が連続するなどの文章としておかしなものはここで弾く
@return string or false
"""
def kanji2katakana(sentence):
    # 漢字をの読みを取得
    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    res = mt.parseToNode(sentence)
    
    result = ""
    old_part = ""

    while res:
        ft = res.feature.split(",")
        # 助詞が連続していないことが前提
        if not (old_part == "助詞" and ft[0] == "助詞"):
            # もともとカタカナだった場合は*が入ってる
            if not ft[-2] == "*":
                result = result+ft[-2]
            else:
                result = result+res.surface
        else:
            return False
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
def count_mora(sentence):
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

    return result, mora_list

"""
# 与えられた漢字混じりの文章のらしさを求める
tuple(word1, word2, sentence, prob)
@return True / False
"""
def judge_research(t):
    threadshold = 0
    #print "judge: %s, %f" % (t[2], float(t[3]))
    if float(t[3]) > threadshold:
        return True
    else:
        return False

"""
# 与えられたテキストとモーラ・音節の一致度を求める
@return True / False
"""
def match_text_vowel(txt, vowel):
    vowel_trim = {
        "a":"ア.*|カ.*|サ.*|タ.*|ナ.*|ハ.*|マ.*|ヤ.*|ラ.*|ワ.*|ガ.*|ザ.*|ダ.*|バ.*|パ.*",
        "i":"イ.*|キ.*|シ.*|チ.*|ニ.*|ヒ.*|ミ.*|リ.*|ギ.*|ジ.*|ヂ.*|ビ.*|ピ.*",
        "u":"ウ.*|ク.*|ス.*|ツ.*|ヌ.*|フ.*|ム.*|ユ.*|ル.*|グ.*|ズ.*|ヅ.*|ブ.*|プ.*",
        "e":"エ.*|ケ.*|セ.*|テ.*|ネ.*|ヘ.*|メ.*|レ.*|ゲ.*|デ.*|ゼ.*|ベ.*|ペ.*",
        "o":"オ.*|コ.*|ソ.*|ト.*|ノ.*|ホ.*|モ.*|ヨ.*|ロ.*|ヲ.*|ゴ.*|ゾ.*|ド.*|ボ.*|ポ.*"
    }
    lowcase_trim = {
        "a":".+ァ|.+ャ",
        "i":".+ィ",
        "u":".+ゥ|.+ュ",
        "e":".+ェ",
        "o":".+ォ|.+ョ"
    }
    # TODO 小文字やンが使われていたら、1モーラとするべきかの判定が必要(リズム等を考慮する)
    # TODO 拗音とかがまざるとズレてるので注意
    # ex. i,6 :バラの研究
    t = unicode(txt.decode('utf-8'))
    for v in vowel:
        trim = vowel_trim[v[0]]
        l_trim = lowcase_trim[v[0]]
        #print len(t), int(v[1]), t
        if len(t) >= int(v[1]):
            mora_num, mora_list = count_mora(txt)
            #print len(t), mora_num
            if len(t) == mora_num:
                # 与えられたtextの文字数とモーラ数が一致
                # 拗音と促音、撥音を含まないと判断
                if not re.match(trim, t[v[1]-1].encode("utf-8")):
                    return False
            else:
                # モーラ数が指定されたモーラ位置より多ければ実行
                #print mora_num, v[1]-1, mora_list[0]
                if mora_num > v[1]-1:
                    #print mora_list[v[1]-1]
                    # 拗音 / 促音 / 撥音を含む場合
                    # 拗音
                    if not re.match(l_trim, mora_list[v[1]-1].encode("utf-8")):
                        return False
                        # 促音と撥音
                    if not re.match(trim, mora_list[v[1]-1].encode("utf-8")):
                        return False
    return True


"""
# 与えられたモーラから、候補文がモーラ数と同等か以下かを判定する
# 同等のモーラと、数以下のモーラのリストを返す
TODO 動的計画法
@return result[], search[]
"""
def search_candidate_from_mora(candidate, mora, vowel):
    result = []
    search = []
    threadshold = 0

    for a in candidate:
        # 与えられたbi-gramの候補(漢字混じり)がモーラ数より大きければその時点で次に行く
        if len(a[2])/3 > mora:
            continue

        # 漢字混じりの文章をカタカナに変換
        katakana = kanji2katakana(a[2])
        if katakana == False:
            continue

        # 生成したテキストと指定母音と場所が一致しているか
        if match_text_vowel(katakana, vowel) == False:
            continue

        #カタカナのモーラ数を判定する
        mora_num, mora_list = count_mora(katakana)
        
        # mora数ピッタリなら結果の配列へ
        # 最後の文字が「ッ」の場合は言葉として不成立
        if mora_num == mora and not (katakana.find("ッ")/3 == len(katakana)/3-1):
            # 文章らしさの確率が閾値以上なら候補とする
            if float(a[3]) > threadshold:
                result.append(a)
        # mora数より少なければ次の検索候補となる
        if mora_num < mora:
            # 検索候補の文章が再検索するに相応しいか判断する
            if judge_research(a):
                search.append(a)
            #print len(s)/3, a[2]

    return result, search

"""
# 単語とモーラから歌詞の候補リストを作成
"""
def create_candidate_list(bigrams, word, mora, vowel):
    result = []
    search = []
    
    # 渡した単語と前方が一致するものをbigramsから返す
    print "searching bigrams...."
    candidate = search_bigram(bigrams, word)

    # モーラ数を調べ、結果と再検索のリストを作成
    result, search = search_candidate_from_mora(candidate, mora, vowel)
    
    num = 1
    for a in search:
        re_candidate = []
        re_result = []
        re_search = []
        
        if a[1]:
            candidate = search_bigram(bigrams, a[1])
        # 再検索なので、配列のsentence部分に以前のbigramを足したものをいれとく
        # TODO 文章らしさの計算のため、確率を求める必要あり。
        for b in candidate:
            if a[3] and b[3]:
                re_candidate.append((b[0], b[1], a[2]+b[1], float(a[3])*float(b[3])))
            #print("tuple(%s, %s, %s)") %(b[0], b[1], a[2]+b[1])
            #print a[2]+b[1]
        re_result, re_search = search_candidate_from_mora(re_candidate, mora, vowel)
        result.extend(re_result)
        search.extend(re_search)
        print "loop: %d, result_length: %d, search_length: %d" % (num, len(result), len(search))
        num = num+1

    return result

"""
# 渡された機械翻訳文と生成された歌詞の単語のベクトル距離を計算して返す
@param lyrics arr[(word1, word2, lyrics, prob)]
@return arr[(lyrics, prob, cos)]
"""
def mean_cos_similarity(model, translation, lyrics_arr):
    result = []
    # 機械翻訳文から名詞と動詞の原形を抜き出す
    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    res = mt.parseToNode(translation)

    translation_words = []
    while res:
        ft = res.feature.split(",")
        if ft[0] == "名詞" or ft[0] == "動詞":
            translation_words.append(ft[6])
        res = res.next

    # 渡された歌詞の全てを調べる
    for lyrics in lyrics_arr:
        # 歌詞から名詞と動詞の原形を抜き出す
        res = mt.parseToNode(lyrics[2])
        lyrics_words = []
        while res:
            ft = res.feature.split(",")
            if ft[0] == "名詞" or ft[0] == "動詞":
                lyrics_words.append(ft[6])
            res = res.next

        # 翻訳文と歌詞の単語を比較し、単語のcos類似を調べる
        # 最もcos類似度が近いものを保持する
        word_cos = []
        for ly_word in lyrics_words:
            old_cos = 0
            for trs_word in translation_words:
                # modelに単語がない場合KeyErrorになる
                #print ly_word, trs_word
                try:
                    cos = model.similarity(unicode(ly_word, "utf-8"), unicode(trs_word, "utf-8"))
                except KeyError:
                    print ly_word, trs_word
                    cos = 0.0
                #print cos
                if old_cos < cos:
                    old_cos = cos
            word_cos.append((ly_word, old_cos))
            #print "max: %f" % old_cos

        # 距離の合計
        result_cos = 0.0
        for a in word_cos:
            #print a[0], a[1]
            result_cos = result_cos + a[1]

        result.append((lyrics[2], lyrics[3], result_cos))

    return result

"""
# 歌詞モデルに従いスコアを計算する
@param lyrics arr[(lyrics, prob, cos)]
@return arr[(lyrics, prob, cos, lyr)]
"""
def calc_lyrics_model(lyrics_arr):
    result = []
    filename = "datas/piapro/dic.txt"
    file = open(filename)
    data = file.read()
    file.close()
    dic = data.split("\n")

    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    for lyrics in lyrics_arr:
        res = mt.parseToNode(lyrics[0])

        # 調べる対象とする単語を抜き出す
        target_wrod = {}
        while res:
            ft = res.feature.split(",")
            if ft[0] == "名詞" or ft[0] == "動詞" or ft[0] == "形容詞":
                target_wrod[res.surface] = target_wrod.get(res.surface, 0)
                # 対象の単語がpiaproの辞書にあるか調べる
                if res.surface in dic:
                    target_wrod[res.surface] = 1
            res = res.next

        # 割合の計算
        num = 0
        for k,v in target_wrod.items():
            if v == 1:
                num = num + 1
            #print k,v

        fl = float(num)/float(len(target_wrod))
        result.append((lyrics[0], lyrics[1], lyrics[2], fl))

    return result

"""
# 文章らしさ、翻訳の確からしさ、歌詞らしさからスコアをつける
@param lyrics arr[(lyrics, prob, cos, lyr)]
@param weight arr[float, float, float]
@return arr[(lyrics, prob, cos, lyr, score)]
"""
def scoring(lyrics_arr, weight):
    result = []

    for lyrics in lyrics_arr:
        score = float(lyrics[1])*weight[0] + float(lyrics[2])*weight[1] + float(lyrics[3])*weight[2]
        result.append((lyrics[0], lyrics[1], lyrics[2], lyrics[3], score))

    return result

def create_lyrics():
    # タプル(英語歌詞、機械翻訳文, モーラ数と音節)
    lyrics = [
        ("Raindrops on roses and, whiskers on kittens", "バラに滴る雨滴,子猫のヒゲ", [6, 5]),
        ("This is the moment", "これは、瞬間です", 5, [5]),
        ("How could I face the faceless days. If I should lose you now", "顔のない日を直面するに可能性。場合は、今あなたを失う必要があります?", [8,6,6]),
    ]

    translate = ["datas/translate/bigram.txt", "datas/translate/vector.model"]
    wiki = ["datas/wiki/bigram.txt", "datas/wiki/vector.model"]

    sources = wiki

    # モデルの読み込み
    model =  word2vec.Word2Vec.load(sources[1])

    # wiki bigramを読み込み、bigramsのリストを生成
    print "creating bigrams...."
    bigrams = create_bigram(sources[0])

    # 翻訳文から候補となる単語を選出

    # 候補となる単語を渡し、モーラを指定し、モーラと一致する歌詞候補のリストを生成
    # TODO 助詞がない歌詞っぽい文章も作れるようにする
    # TODO 言語モデルの確率をちゃんと求める

    #l = "これは、瞬間です"
    #vowel = [("a", 3),("a", 5)]

    l = "バラに滴る雨滴"
    #l = "子猫のヒゲ"
    vowel = [("o", 3)]
    #vowel = []
    print "creating candidate list...."
    candidate_list = create_candidate_list(bigrams, "バラ", 6, vowel)

    # 候補のリストから、翻訳文と生成文を与え翻訳モデルのスコアを計算する
    # TODO 翻訳モデルの求め方を再度定義すべき
    candidate_list = mean_cos_similarity(model, l, candidate_list)

    # 歌詞モデルのスコアを計算する
    candidate_list = calc_lyrics_model(candidate_list)

    # 重み付けをして候補の順位を決定する
    # 言語モデル / 翻訳モデル / 歌詞モデル
    weight = [1.0, 0.0, 0.0]
    print weight
    candidate_list = scoring(candidate_list, weight)

    # cos類似度で並べ替え
    #candidate_list = sorted(candidate_list, key=lambda x: float(x[2]))
    # 言語モデルで並べ替え
    #candidate_list = sorted(candidate_list, key=lambda x: float(x[1]))
    # スコアで並べ替え
    candidate_list = sorted(candidate_list, key=lambda x: float(x[4]))

    # 歌詞候補の一覧
    for a in candidate_list:
        print a[0], a[1], a[2], a[3], a[4]
    print "%d candidate" % len(candidate_list)

    # 実験結果用 いらない
    weight = [1.0, 0.0, 0.0]
    print weight
    result(candidate_list, weight)

    weight = [0.0, 1.0, 0.0]
    print weight
    result(candidate_list, weight)

    weight = [0.0, 0.0, 1.0]
    print weight
    result(candidate_list, weight)

    weight = [0.4, 0.3, 0.3]
    print weight
    result(candidate_list, weight)

    weight = [0.6, 0.3, 0.1]
    print weight
    result(candidate_list, weight)

    weight = [0.5, 0.5, 0.0]
    print weight
    result(candidate_list, weight)

    weight = [0.6, 0.4, 0.0]
    print weight
    result(candidate_list, weight)

def result(candidate_list, weight):
    candidate_list = scoring(candidate_list, weight)

    # スコアで並べ替え
    candidate_list = sorted(candidate_list, key=lambda x: float(x[4]))

    # 歌詞候補の一覧
    for i in range(0, 5):
        a = candidate_list[i]
        print a[0], a[1], a[2], a[3], a[4]
    print "%d candidate" % len(candidate_list)


if __name__ == '__main__':
    # 楽曲解析

    # 歌詞の作成
    create_lyrics()

    #tf = match_text_vowel("バラノケンキュウ", [("i", 6)])
    #print tf

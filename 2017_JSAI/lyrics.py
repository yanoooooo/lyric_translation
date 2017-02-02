#coding:utf-8
#機械翻訳文から歌詞を生成する

import nltk
import MeCab
import jaconv
import difflib

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
# 与えられたカタカナの文章のモーラ数を返す
# 促音や撥音の処理もここで
@return int
"""
def count_mora(sentence):
    lst = ["ッ", "ャ", "ュ", "ョ", "ン"]
    result = len(sentence)/3

    for a in lst:
        if a in sentence:
            result = result - 1

    return result

"""
# 与えられた漢字混じりの文章のらしさを求める
tuple(word1, word2, sentence, prob)
@return True / False
"""
def judge_research(t):
    threadshold = 0.001
    #print "judge: %s, %f" % (t[2], float(t[3]))
    if float(t[3]) > threadshold:
        return True
    else:
        return False

"""
# 与えられたモーラから、候補文がモーラ数と同等か以下かを判定する
# 同等のモーラと、数以下のモーラのリストを返す
TODO 動的計画法
@return result[], search[]
"""
def search_candidate_from_mora(candidate, mora):
    result = []
    search = []
    threadshold = 0.0001

    for a in candidate:
        # 与えられたbi-gramの候補(漢字混じり)がモーラ数より大きければその時点で次に行く
        if len(a[2])/3 > mora:
            continue

        # 漢字混じりの文章をカタカナに変換
        katakana = kanji2katakana(a[2])
        if katakana == False:
            continue

        #カタカナのモーラ数を判定する
        mora_num = count_mora(katakana)
        
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
    # TODO トライ木を使った方が良い？？ -> https://github.com/IshitaTakeshi/Louds-Trie
    result = []
    search = []
    
    # 渡した単語と前方が一致するものをbigramsから返す
    print "searching bigrams...."
    candidate = search_bigram(bigrams, word)

    # モーラ数を調べ、結果と再検索のリストを作成
    result, search = search_candidate_from_mora(candidate, mora)
    
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
            re_candidate.append((b[0], b[1], a[2]+b[1], float(a[3])*float(b[3])))
            #print("tuple(%s, %s, %s)") %(b[0], b[1], a[2]+b[1])
            #print a[2]+b[1]
        re_result, re_search = search_candidate_from_mora(re_candidate, mora)
        result.extend(re_result)
        search.extend(re_search)
        print "loop: %d, resutl_length: %d, search_length: %d" % (num, len(result), len(search))
        num = num+1

    return result

if __name__ == '__main__':
    # タプル(英語歌詞、機械翻訳文, モーラ数と音節)
    lyrics = [
        ("Raindrops on roses and, whiskers on kittens", "バラに滴る雨滴,子猫のヒゲ", [6, 5]),
        ("This is the moment", "これは、瞬間です", 5, [5]),
        ("How could I face the faceless days. If I should lose you now", "顔のない日を直面するに可能性。場合は、今あなたを失う必要があります?", [8,6,6]),
    ]

    translate = ["datas/translate/bigram.txt"]
    wiki = ["datas/wiki/bigram.txt"]

    sources = translate

    # wiki bigramを読み込み、bigramsのリストを生成
    print "creating bigrams...."
    bigrams = create_bigram(sources[0])

    # 翻訳文から候補となる単語を選出

    # 候補となる単語を渡し、モーラを指定し、モーラと一致する歌詞候補のリストを生成
    # TODO 助詞がない歌詞っぽい文章も作れるようにする
    # TODO 母音の指定
    vowel = [("あ", 1), ("お", 3)]
    print "creating candidate list...."
    candidate_list = create_candidate_list(bigrams, "バラ", 5, vowel)

    # 候補のリストから、元の文章と類似度が高いものを選出する

    #TODO difflib使ってるけど、他で類似度計算するべき -> doc2vecとか？
    # 歌詞候補の一覧
    l = "バラに滴る雨滴"
    for a in candidate_list:
        #diff = difflib.SequenceMatcher(None, l.strip(), a[2].strip()).ratio()
        #if diff > 0.6:
            #print a[2]+b[2]
        print a[2], a[3]
    print "%d candidate" % len(candidate_list)

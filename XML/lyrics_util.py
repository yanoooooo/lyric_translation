#coding:utf-8
#機械翻訳文から歌詞を生成する

import nltk
import MeCab
import jaconv
import re
from gensim.models import word2vec
import count_mora as cm
import language_processing as lp

class LyricsUtil:
    def __init__(self, resources):
        # モデルの読み込み
        self.vector =  word2vec.Word2Vec.load(resources["vector"])
        
        # bigramの作成
        print "creating bigrams...."
        self.bigrams = self.__create_bigram(resources)

    """
    # ファイルからbigramを読み込んでそのリストを返す
    @return array[tuple(word1, word2, freq), tuple...]
    """
    def __create_bigram(self, resources):
        result = []
        # (word1, word2, frequency)
        for row in open(resources["bigram"]).readlines():
            row = row.strip().split(',')
            result.append(tuple(row))
        print "DONE...%d objects created" % len(result)

        return result

    """
    # 単語とモーラから歌詞の候補リストを作成
    """
    def __create_candidate_list(self, word, mora, vowel):
        result = []
        search = []
        
        # 渡した単語と前方が一致するものをbigramsから返す
        print "searching bigrams...."
        candidate = self.__search_bigram(word)
        
        # モーラ数を調べ、結果と再検索のリストを作成
        result, search = self.__search_candidate_from_mora(candidate, mora, vowel)
        
        num = 1
        for a in search:
            re_candidate = []
            re_result = []
            re_search = []
            
            if a[1]:
                candidate = self.__search_bigram(word)
            # 再検索なので、配列のsentence部分に以前のbigramを足したものをいれとく
            # TODO 文章らしさの計算のため、確率を求める必要あり。
            for b in candidate:
                if a[3] and b[3]:
                    re_candidate.append((b[0], b[1], a[2]+b[1], float(a[3])*float(b[3])))
                #print("tuple(%s, %s, %s)") %(b[0], b[1], a[2]+b[1])
                #print a[2]+b[1]
            re_result, re_search = self.__search_candidate_from_mora(re_candidate, mora, vowel)
            result.extend(re_result)
            search.extend(re_search)
            print "loop: %d, result_length: %d, search_length: %d" % (num, len(result), len(search))
            num = num+1

        return result

    """
    # 与えられた単語と前方が一致するbigramのリストを返す
    @return array[tuple(word1, word2, sentence, freq), tuple...]
    """
    def __search_bigram(self, word):
        result = []
        for a in self.bigrams:
            if a[0] == word:
                result.append((a[0], a[1], a[0]+a[1], a[2]))
                #print("w1: %s, w2: %s, sentence: %s, freq: %s") % (a[0], a[1], a[0]+a[1], a[2])
        return result

    """
    # 与えられたモーラから、候補文がモーラ数と同等か以下かを判定する
    # 同等のモーラと、数以下のモーラのリストを返す
    TODO 動的計画法
    @param candidate array[tuple(word1, word2, sentence, freq), tuple...]
    @return result[], search[]
    """
    def __search_candidate_from_mora(self, candidate, mora, vowel):
        result = []
        search = []
        threadshold = 0.000011099

        for a in candidate:
            sentence = unicode(a[2].decode("utf-8"))
            # 与えられたbi-gramの候補(漢字混じり)がモーラ数より大きければその時点で次に行く
            if len(sentence) > mora:
                continue

            # 漢字混じりの文章をカタカナに変換
            katakana = lp.kanji2katakana(sentence.encode("utf-8"), True)
            
            if katakana == False:
                continue

            # 生成したテキストと指定母音と場所が一致しているか
            if self.__match_text_vowel(katakana, vowel) == False:
                continue
            
            #カタカナのモーラ数を判定する
            mora_num = cm.count_mora(katakana)
            mora_list = cm.create_mora_list(katakana)
            
            # mora数ピッタリなら結果の配列へ
            # 最後の文字が「ッ」の場合は言葉として不成立
            if mora_num == mora and not (katakana.find("ッ")/3 == len(katakana)/3-1):
                #print mora_num, mora, katakana.find("ッ")/3, len(katakana)/3-1
                # 文章らしさの確率が閾値以上なら候補とする
                #print "candidate: %s, %f" % (sentence, float(a[3]))
                if float(a[3]) > threadshold:
                    result.append(a)
            # mora数より少なければ次の検索候補となる
            if mora_num < mora:
                # TODO 検索候補の文章が再検索するに相応しいか判断する
                if self.__judge_research(a):
                    search.append(a)

        return result, search

    """
    # 与えられた漢字混じりの文章のらしさを求める
    tuple(word1, word2, sentence, prob)
    @return True / False
    """
    def __judge_research(self, arr):
        #threadshold = 0.000001
        threadshold = 0.000114849 #average
        #print "judge: %s, %f" % (t[2], float(t[3]))
        if float(arr[3]) > threadshold:
            return True
        else:
            return False

    """
    # 与えられたテキストとモーラ・音節の一致度を求める
    @return True / False
    """
    def __match_text_vowel(self, katakana, vowel):
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
        t = unicode(katakana.decode('utf-8'))
        for v in vowel:
            trim = vowel_trim[v[0]]
            l_trim = lowcase_trim[v[0]]
            #print len(t), int(v[1]), t
            if len(t) >= int(v[1]):
                mora_num = cm.count_mora(katakana)
                mora_list = cm.create_mora_list(katakana)
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
    # 渡された機械翻訳文と生成された歌詞の単語のベクトル距離を計算して返す
    @param lyrics arr[(word1, word2, lyrics, prob)]
    @return arr[(lyrics, prob, cos)]
    """
    def __mean_cos_similarity(self, translation, lyrics_arr):
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
                        cos = self.vector.similarity(unicode(ly_word, "utf-8"), unicode(trs_word, "utf-8"))
                    except KeyError:
                        #print ly_word, trs_word
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
    def __calc_lyrics_model(self, lyrics_arr):
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
    def __scoring(self, lyrics_arr, weight):
        result = []

        for lyrics in lyrics_arr:
            score = float(lyrics[1]) + float(lyrics[2]) + float(lyrics[3])*weight
            result.append((lyrics[0], lyrics[1], lyrics[2], lyrics[3], score))

        return result

    """
    # 指定されたモーラ、母音から歌詞を作成する
    @param word str
    @param mora int
    @param vowel array[("o", 3),("a", 5)....]
    @return str
    """
    def create_lyrics(self, word, translate, mora, vowel):
        # 候補となる単語を渡し、モーラを指定し、モーラと一致する歌詞候補のリストを生成
        # TODO 助詞がない歌詞っぽい文章も作れるようにする
        # TODO 言語モデルの確率をちゃんと求める

        
        #vowel = [("a", 3),("a", 5)]
        vowel = [("a", 5)]
        
        print "creating candidate list...."
        candidate_list = self.__create_candidate_list(word, mora, vowel)
        
        # 候補のリストから、翻訳文と生成文を与え翻訳モデルのスコアを計算する
        # TODO 翻訳モデルの求め方を再度定義すべき
        candidate_list = self.__mean_cos_similarity(translate, candidate_list)
        
        # 歌詞モデルのスコアを計算する
        candidate_list = self.__calc_lyrics_model(candidate_list)
        
        # 重み付けをして候補の順位を決定する
        # 言語モデル / 翻訳モデル / 歌詞モデル
        weight = 1.0
        #print weight
        candidate_list = self.__scoring(candidate_list, weight)

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

        if len(candidate_list) > 0:
            return candidate_list[-1][0]
        else:
            return False

if __name__ == '__main__':
    # 楽曲解析

    r = {"corpus": "datas/novel/corpus.txt", "bigram": "datas/novel/bigram.txt", "vector": "datas/novel/vector.model"}
    lu = LyricsUtil(r)

    # 歌詞の作成
    #vowel = [("a", 3),("a", 5)]
    vowel = []
    result = lu.create_lyrics("幸せ", "幸せな家庭", 8, vowel)

    print result

    #tf = match_text_vowel("バラノケンキュウ", [("i", 6)])
    #print tf

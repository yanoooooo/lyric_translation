#coding:utf-8
# word2vecを用いて単語をベクトル化し、その距離が近い単語を求める
from gensim.models import word2vec
import logging
import sys

def create_vect(filenames):
    # 進捗表示用
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # Word2Vecの学習に使用する分かち書き済みのテキストファイルの準備
    sentences = word2vec.Text8Corpus(filenames[0])

    # Word2Vecのインスタンス作成
    # sentences : 対象となる分かち書きされているテキスト
    # size      : 出力するベクトルの次元数
    # min_count : この数値よりも登場回数が少ない単語は無視する
    # window    : 一つの単語に対してこの数値分だけ前後をチェックする
    model = word2vec.Word2Vec(sentences, size=200, min_count=20, window=15)

    print "Done!!!"

    # 学習結果を出力する
    model.save(filenames[1])


def word_cos(filename, posi, nega=[], n=10):
    # 学習済みモデルのロード
    model = word2vec.Word2Vec.load(filename)
    cnt = 1 # 表示した単語の個数カウント用
    # 学習済みモデルからcos距離が最も近い単語n個(topn個)を表示する
    result = model.most_similar(positive = posi, negative = nega, topn = n)
    for r in result:
        print cnt,'　', r[0],'　', r[1]
        cnt += 1

def similar(word1, word2, filename):
    model = word2vec.Word2Vec.load(filename)
    print word1, word2
    try:
        print model.similarity(word1, word2)
    except KeyError:
        print "oooops"

if __name__ == '__main__':
    piapro = ['datas/piapro/corpus.txt', 'datas/piapro/vector.model']
    translate = ['datas/translate/corpus.txt', 'datas/translate/vector.model']
    wiki = ['datas/wiki/corpus.txt', 'datas/wiki/vector.model']

    datas = translate

    # モデルの作成
    #create_vect(datas)

    # 入力された単語から近い単語をn個表示する
    word = "香水"
    word = unicode(word, 'utf-8')
    #word_cos(datas[1], [word])

    similar(u"香水", u"バラ", datas[1])


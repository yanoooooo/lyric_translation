#!/bin/sh

# wikiのディレクトリを作成
dir=./XML/datas/wiki; [ ! -e $dir ] && mkdir -p $dir

# wikiコーパスの取得
curl https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-articles.xml.bz2 -o jawiki-latest-pages-articles.xml.bz2

# コーパスをパースするリポジトリをclone
git clone https://github.com/attardi/wikiextractor

# 実行
python wikiextractor/WikiExtractor.py jawiki-latest-pages-articles.xml.bz2

# 1つのファイルにまとめる
cat text/*/* > jawiki_org.txt

# トリミング
cat ./jawiki_org.txt | sed -e 's/<.*>//g' | sed -e '/^ *$/d' > ./jawiki.txt

# 不要なファイルの削除
sudo rm ./jawiki-latest-pages-articles.xml.bz2
sudo rm ./jawiki_org.txt
sudo rm -r ./wikiextractor
sudo rm -r ./text

# mecabで分かち書き
# 環境によって辞書の位置が変わるので注意
mecab -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/ -Owakati -b 781361152 jawiki.txt > ./XML/datas/wiki/corpus.txt

# 不要なファイルの削除
sudo rm ./jawiki.txt

# bigramの作成
python ./setup/create_bigram.py

# word2vec modelの作成
python ./setup/create_vector_model.py
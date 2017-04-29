# translation_lyrics
英語の歌詞を伴う単旋律のMusicXMLを日本語のMusicXMLに変換する

## setup
* mecabのインストール
* mecab-ipadic-neologdのインストール
* wiki辞書の用意
* 必要なpythonライブラリのインストール

### mecabのインストール
mac, windows, linuxなど環境によって異なる
以下のコマンドが通るようにweb等で検索してインストールを行うこと
```
$ which mecab
/usr/local/bin/mecab
```

### mecab-ipadic-neologdのインストール
mecab-ipadic-neologdを使えばweb上から得た新しい単語の解析も可能になる。
mac版は以下を参考にすること
http://cantabilemusica.blogspot.jp/2017/01/mecab-ipadic-neologd.html

以下のコマンドが通り、形態素解析ができれば問題ない。
```
$ mecab -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/
```

### wiki辞書の用意
2GB近くあるため、gitには上げていない。
以下のコマンドをrootディレクトリで実行することで、./XML/datas/wikiに5つのファイルを作成する。
時間がかかる上に、環境によってはmecab-ipadic-neologdの場所が違うので注意。
```
$ sh setup.sh
```
以下のエラーが出る場合は -b の後の指定バイト数を変更すること。
http://cantabilemusica.blogspot.jp/2017/04/input-buffer-overflow-line-is-split-use.html
```
input-buffer overflow. The line is split. use -b #SIZE option.
```
* bigram.txt
* copus.txt
* vector.model
* vector.model.syn1neg.npy
* vector.model.wv.syn0.npy

が出来ればOK

### 必要なpythonライブラリのインストール
rootディレクトリで以下のコマンドを実行
```
$ pip install -r requirements.txt
```
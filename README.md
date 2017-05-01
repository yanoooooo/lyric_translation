# translation_lyrics
英語の歌詞を伴う単旋律のMusicXMLを日本語のMusicXMLに変換する
* setup
* 楽譜の確認
* プログラムの実行

## setup
* mecabのインストール
* mecab-ipadic-neologdのインストール
* 必要なpythonライブラリのインストール
* wiki辞書の用意

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

### 必要なpythonライブラリのインストール
rootディレクトリで以下のコマンドを実行
```
$ sudo pip install -r requirements.txt
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
※ pipがインストールされている前提。pipとは、pythonのライブラリ管理コマンド。
rootディレクトリで以下のコマンドを実行
```
$ sudo pip install -r requirements.txt
```
必要最低限しか入れていないので、もしプログラム実行時に以下のようなエラーがでた場合は内容にそってmoduleをinstallすること。
```
# jaconvというmoduleが無い
ImportError: No module named jaconv

$ pip install jaconv
```

## 楽譜の確認
* MuseScoreのダウンロード
* 譜面の確認

### MuseScoreのダウンロード
楽譜作成ツールをダウンロードする
https://musescore.org/ja

### 譜面の確認
./XML/datas/score 配下にある *.xml ファイルを読み込んで見る
エラー無く表示されればOK

## プログラムの実行
pythonプログラムを実行し、実際に日本語楽譜が作成されるか確認する。
成功すれば、./XML/test.xml というファイルが生成されるので、名前を付け替えるなりして保管。
MuseScoreで読み込んで、実際に楽譜がどうなっているかを確認できる。
```
$ cd ./XML
$ python main.py <日本語に変換したい楽譜のファイル名>

# ロンドン橋の作成例
$ python main.py ./datas/score/London_Bridge.xml
creating bigrams....
DONE...360142 objects created
ロンドン橋落ちる, 歌詞モーラ: 7, 許容モーラ: 7
落ちる, 歌詞モーラ: 3, 許容モーラ: 3
落ちる, 歌詞モーラ: 3, 許容モーラ: 3
ロンドン橋落ちる, 歌詞モーラ: 7, 許容モーラ: 7
Finished reading file....
Finished morphological analysis....
Finished spliting word....
マイフェアレディ, 歌詞モーラ: 6, 許容モーラ: 4
more
7 ロンドン橋落ちる
3 落ちる
3 落ちる
7 ロンドン橋落ちる
6 マイフェアレディ
7 London bridge is falling down.
3 falling down.
3 falling down.
7 London bridge is falling down.
4 my fair lady.
Done!
```


#coding:utf-8
# MusicXMLを読み込み、英語を日本語にしたXMLを返す

import read_xml as rx

if __name__ == '__main__':
    # XMLの読み込み
    # [(mora_num, "lyrics"), (mora_num, "lyrics").....]
    mora_lyrics = rx.read_xml()
    print mora_lyrics

    # 原言語を翻訳機にかける
    # [(mora_num, "lyrics", "歌詞"), (mora_num, "lyrics", "歌詞").....]
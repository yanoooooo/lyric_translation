#coding:utf-8
# MusicXMLを読み込み、英語を日本語にしたXMLを返す

import read_xml as rx
import translate as trs

if __name__ == '__main__':
    # XMLの読み込み
    # [(mora_num, "lyrics"), (mora_num, "lyrics").....]
    mora_src = rx.read_xml()
    #print mora_src

    # 原言語を翻訳機にかける
    # [(mora_num, "lyrics", "歌詞"), (mora_num, "lyrics", "歌詞").....]
    mora_src_obj = trs.translate(mora_src)
    for a in mora_src_obj:
        print a[1], a[2]
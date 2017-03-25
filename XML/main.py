#coding:utf-8
# MusicXMLを読み込み、英語を日本語にしたXMLを返す

import read_xml as rx
import translate as trs
import count_mora as cm

if __name__ == '__main__':
    # XMLの読み込み
    # [(mora_num, "lyrics"), (mora_num, "lyrics").....]
    mora_src = rx.read_xml()
    #print mora_src

    # 原言語を翻訳機にかける
    # [(mora_num, "lyrics", "翻訳"), (mora_num, "lyrics", "翻訳").....]
    mora_src_obj = trs.translate(mora_src)
    #for a in mora_src_obj:
    #    print a[1], a[2]

    # 翻訳した日本語のモーラ数を数える
    # [(mora_num, "lyrics", "翻訳", obj_mora}), (mora_num, "lyrics", "翻訳", obj_mora).....]
    mora_src_obj_om = cm.count_mora(mora_src_obj)
    for a in mora_src_obj_om:
        print("%d: %s") % (a[0], a[1])
        print("%d: %s") % (a[3], a[2])
        print "------"
    
    # 翻訳のモーラが3以上多い場合は、助詞を抜く等の操作をする

    # MusicXMLの出力だが、モーラが合わない場合はどこかの音符を分割する
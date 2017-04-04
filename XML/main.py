#coding:utf-8
# MusicXMLを読み込み、英語を日本語にしたXMLを返す

import read_xml as rx
import translate as trs
import count_mora as cm
import language_processing as lp

permission_mora = 0 # 溢れるのを許容するモーラ数

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
    # [(mora_num, "lyrics", "翻訳", obj_mora), (mora_num, "lyrics", "翻訳", obj_mora).....]
    mora_src_obj_om = []
    for mso in mora_src_obj:
        obj_mora = cm.count_mora(mso[2])
        mora_src_obj_om.append((mso[0], mso[1], mso[2], obj_mora))
    #for a in mora_src_obj_om:
    #    print("%d: %s") % (a[0], a[1])
    #    print("%d: %s") % (a[3], a[2])
    #    print "------"
    
    # 翻訳のモーラが指定数以上の場合は、助詞を抜く等の操作を試みる
    # [[lyrics, mora], [lyrics, mora]]
    #たぷるは更新できないいいいいいいいいいいいいい
    lyrics = []
    process = 0
    for num in range(0, len(mora_src_obj_om)):
        while True:
            # 許容モーラ数になるまで文字数を減らす処理を続ける
            if mora_src_obj_om[num][0]+permission_mora < mora_src_obj_om[num][3]:
                # ですます調を削除
                # ます、の前の独立した動詞まで遡り、その原形を取得する
                if process == 0:
                    lyrics.append(lp.delete_honolific(mora_src_obj_om[num][2]))
                # 「だ」の断定を削除
                #else if process == 1:
                # 助詞を省略
                #else if process == 2:
                # 文章生成
                #else if process == 3:
                process = process+1
            else:
                break
            
    for a in lyrics:
        print a

    # MusicXMLの出力だが、モーラが合わない場合はどこかの音符を分割する
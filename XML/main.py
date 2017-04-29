#coding:utf-8
# MusicXMLを読み込み、英語を日本語にしたXMLを返す

import xml_util as rx
import translate as trs
import count_mora as cm
import language_processing as lp
import lyrics_util

# 言語資源
novel = {"corpus": "datas/novel/corpus.txt", "bigram": "datas/novel/bigram.txt", "vector": "datas/novel/vector.model"}
wiki = {"corpus": "datas/wiki/corpus.txt", "bigram": "datas/wiki/bigram.txt", "vector": "datas/wiki/vector.model"}
resource = novel

permission_mora = 0 # 溢れるのを許容するモーラ数
reduce_mora = 3 #減るのを許容するモーラ数
output_xml = "./test.xml" #出力するxml名

if __name__ == '__main__':
    # create class
    ly_util = lyrics_util.LyricsUtil(resource)

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
        obj_mora = cm.kanji_count_mora(mso[2])
        mora_src_obj_om.append((mso[0], mso[1], mso[2], obj_mora))
    #for a in mora_src_obj_om:
    #    print("%d: %s") % (a[0], a[1])
    #    print("%d: %s") % (a[3], a[2])
    #    print "------"
    
    # 翻訳のモーラが指定数以上の場合は、助詞を抜く等の操作を試みる
    # lyrics = arr[("lyrics", lyrics_mora), ("lyrics", lyrics_mora)...]
    lyrics = []
    lyrics_mora = 0
    process = 0
    for num in range(0, len(mora_src_obj_om)):
        process = 0
        # 句読点は抜く
        l = mora_src_obj_om[num][2].replace("、", "")
        lyrics_mora = mora_src_obj_om[num][3]
        while True:
            # 許容モーラ数になるまで文字数を減らす処理を続ける
            if mora_src_obj_om[num][0]+permission_mora < lyrics_mora:
                # ですます調を削除
                # ます、の前の独立した動詞まで遡り、その原形を取得する
                if process == 0:
                    l = lp.delete_honolific(l)
                    lyrics_mora = cm.kanji_count_mora(l)
                # 「だ」の断定を削除
                elif process == 1:
                    l = lp.delete_honolific(l)
                    lyrics_mora = cm.kanji_count_mora(l)
                # 助詞を省略
                elif process == 2:
                    l = lp.delete_particle(l)
                    lyrics_mora = cm.kanji_count_mora(l)
                # 文章生成
                elif process == 3:
                    # 作成で今までの歌詞が失われるので保存しておく
                    lyrics_old = l
                    # 文章中の単語にtf-idf値を付与する
                    # WARN tf-idfだけは小節をモデルとして使う
                    ti = lp.tf_idf(l, novel)
                    # TODO 同じtf-idfの値があったらどうするか？？？？？？？？？？
                    l = ti[0][0]
                    lyrics_mora = cm.kanji_count_mora(l)

                    # モーラ数が許容する減少モーラより少ない場合は文章生成
                    if lyrics_mora < mora_src_obj_om[num][0]+permission_mora-reduce_mora:
                        vowel = []
                        l = ly_util.create_lyrics(l, mora_src_obj_om[num][2], mora_src_obj_om[num][0], vowel)
                        if l != False:
                            lyrics_mora = cm.kanji_count_mora(l)
                        else:
                            # 歌詞作成でどうにもならないので、今までのを返す
                            l = lyrics_old
                            lyrics_mora = cm.kanji_count_mora(l)
                        # TODO 母音の限定は？？？？？？？？？？？？
                # TODO 一人称や代名詞を省略？？？？？？？？？？？？
                elif process == 4:
                    # これ以上減らせないので諦める
                    break
                process = process+1
            else:
                break
        print("%s, 歌詞モーラ: %d, 許容モーラ: %d") % (l, lyrics_mora, mora_src_obj_om[num][0]+permission_mora)
        lyrics.append((lyrics_mora, l))

    # MusicXMLの出力
    rx.create_xml(lyrics, output_xml)


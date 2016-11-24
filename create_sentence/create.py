#coding:utf-8
#与えられたキーワードから文章を生成し、要約するプログラム
import MeCab

def extract_keyword(s):
    words = []
    result = []
    mt = MeCab.Tagger("-Ochasen")
    res = mt.parseToNode(s)
    while res:
        if res.surface:
            words.append(res.surface)
        ft = res.feature.split(",")
        if ft[0] == "名詞" or ft[0] == "動詞":
            #print res.surface, ft[0]
            result.append(res.surface)
        res = res.next
    return result

if __name__ == '__main__':
    s = "旅客の安全検査を一部簡素化する方向で検討する。"

    # キーワード抽出
    keywords = extract_keyword(s)
    print ",".join(keywords)

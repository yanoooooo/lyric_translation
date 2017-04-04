#coding:utf-8

import MeCab

# ですます調を削除
# ます、の前の独立した動詞まで遡り、その原形を取得する
def delete_honolific(sentence):
    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    res = mt.parseToNode(sentence)

    # [(要素, 品詞, 詳細な品詞, 原形),("落ち", 動詞, 自立, "落ちる")....]
    elements = []
    while res:
        ft = res.feature.split(",")
        elements.append((res.surface, ft[0], ft[1], ft[6]))
        #print res.surface, res.feature
        res = res.next

    # BOS/EOSの削除
    elements.pop(0)
    elements.pop()

    result = ""
    org = ""
    if elements[-1][0] == "です" or elements[-1][0] == "ます":
        # 動詞があれば、その原形を取得する
        i = 2
        for elem in reversed(elements[:-1]):
            if (elem[1] == "動詞" and elem[2] == "自立") or elem[1] == "助動詞":
                org = elem[3]
                for num in range(0, len(elements)-i):
                    result = result + elements[num][0]
                break
            i = i + 1

        # 「必要です」のように動詞が無い場合
        if result == "" and elements[-1][0] == "です":
            for a in elements[:-1]:
                result = result + a[0]
            result = result + "だ"

    result = result + org

    # 空だった場合は、sentenceをそのまま返す
    if result == "":
        result = sentence

    return result

# 「だ」の断定を削除
def delete_da(sentence):
    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    res = mt.parseToNode(sentence)

    # [(要素, 品詞, 詳細な品詞, 原形),("落ち", 動詞, 自立, "落ちる")....]
    elements = []
    while res:
        ft = res.feature.split(",")
        elements.append((res.surface, ft[0], ft[1], ft[6]))
        #print res.surface, res.feature
        res = res.next

    # BOS/EOSの削除
    elements.pop(0)
    elements.pop()

    result = ""
    if elements[-1][0] == "だ" and elements[-1][1] == "助動詞":
        for a in elements[:-1]:
            result = result + a[0]

    if result == "":
        result = sentence

    return result

# 助詞を省略
def delete_particle(sentence):
    mt = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    res = mt.parseToNode(sentence)

    # [(要素, 品詞, 詳細な品詞, 原形),("落ち", 動詞, 自立, "落ちる")....]
    elements = []
    while res:
        ft = res.feature.split(",")
        elements.append((res.surface, ft[0], ft[1], ft[6]))
        #print res.surface, res.feature
        res = res.next

    # BOS/EOSの削除
    elements.pop(0)
    elements.pop()

    result = ""
    for a in elements:
        if a[1] != "助詞":
            result = result + a[0]

    return result

if __name__ == '__main__':
    arr = [
        "さまざまなマニュアル本に、恋を成功させるためのテクニックが紹介されています",
        "しかし、それは恋の達人たちの必殺技であることが多く、タイミングや雰囲気、しぐさや口調といった様々な要素を考慮する必要があります",
        "そもそもモテ子の恋の駆け引きは、自分に合った素敵な彼を選別したり、彼との恋にエッセンスを加えたりする手段なのです",
        "でも、その駆け引きには、タイミングと経験が必要です",
        "だから、「男運悪いかも？」と思う女性が、突然モテ子のマネをしても、経験不足から失敗してしまいます",
        "ましてや、その駆け引きのために、悪い男を引き寄せている場合もあります。素敵な男性は、未熟な駆け引きには乗って来ないからです",
        "駆け引きをするよりも自分の気持ちに素直になりましょう",
        "「愛しているなら○○してくれるはず」ではなく、「愛しているから○○する」と自分の気持ちを表現するのです",
        "何かをしてほしければ、「私のことが好きなら気付いてくれる」と待つのではなく、上手にヒントを出したり、直接お願いしたりしてみましょう",
        "勇気がいることですが、気取ったり、自分を良く見せようとつくろうのではなく、ありのままの自分を出すのです",
        "実は、上手に気持ちを伝え、甘え上手である人は、既に男運の良いモテ子だともいえます。だから、これはモテ子への近道でもあるのです"
    ]

    for a in arr:
        delete_particle(a)

    delete_particle("ロンドン橋が必要だ")


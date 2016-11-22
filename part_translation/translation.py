#coding:utf-8
# 英文と部分的表現の2つを入力すると翻訳する
import MeCab
import jaconv
import networkx as nx
from math import exp, expm1
import matplotlib.pyplot as plt

word_importantance = 0.7

def grep_corpus(str):
    filename = "./data/parallel.txt"
    ld = open(filename)
    lines = ld.readlines()
    ld.close()

    result = []
    for line in lines:
        if line.find(str) >= 0:
            arr = line[:-1].split("\t")
            result.append(arr[0].replace("、","").replace("。",""))
            print line[:-1]

    return result

# @param list array[]
def split_word(list):
    result = []
    words = []
    mt = MeCab.Tagger("-Ochasen")
    for i in range(len(list)):
        res = mt.parseToNode(list[i])
        
        while res:
            if res.surface:
                words.append(res.surface)
            #print res.surface
            #print res.feature
            res = res.next
        
        result.append(words)
        words = []
        #print jaconv.kata2hira(result.decode('utf-8')).encode('utf-8')
    #print result
    return result

# @param list array[][]
def joint_word(list):
    word_list = list
    req = {}
    result = []
    word_num = 0
    
    # 各単語の出現頻度
    for i in range(len(word_list)):
        for j in range(len(word_list[i])):
            word = word_list[i][j]
            req[word] = req.get(word, 0) + 1

    # 全部の単語数
    word_num = len(req)

    # 重要度の算出
    for k,v in req.items():
        score = float(v)/float(word_num)
        #print score
        if score > word_importantance:
            result.append(k)

    return result

# @param list array[][]
def create_word_graph(list, sentence):
    # 重要単語の抽出
    j_words = joint_word(list)
    word_list = list
    graph = nx.DiGraph()

    # ノードの結合
    for i in range(len(word_list)):
        num = 0
        while num < len(word_list[i]):
            if word_list[i][num] in j_words:
                word_list[i][num-1] = word_list[i][num-1] + word_list[i][num]
                del word_list[i][num]
            else:
                num += 1

    # add nodes
    graph.add_node("start")
    graph.add_node("end")
    for i in range(len(word_list)):
        graph.add_nodes_from(word_list[i])
    

    # add edge
    for i in range(len(word_list)):
        word_list[i].insert(0, "start")
        word_list[i].append("end")
        for j in range(len(word_list[i])-1):
            graph.add_edge(word_list[i][j], word_list[i][j+1], weight=0.0)
    print "add edge....."

    # エッジの重みの取得
    graph = calc_weight(graph, word_list, sentence)
    print "calc weight....."

    return graph

# return [(a, b, weight),(a, b, weight)]
def calc_weight(graph, list, sentence):
    edges_weight = []
    edge_sum = {}
    src_id_filename = "./data/giza/trn.src.vcb"
    trg_id_filename = "./data/giza/trn.trg.vcb"
    prob_data_filename = "./data/giza/t3.final"
    word_list = list
    src_arr = sentence.split(" ")
    edge_list = {}
    src_ids = {}
    trg_ids = {}
    prob_datas = {}
    
    # データからidと単語をk-vで持つようにする
        # 原語のデータ
    ld = open(src_id_filename)
    lines = ld.readlines()
    ld.close()

    for line in lines:
        arr = line.split(" ")
        src_ids[arr[1]] = src_ids.get(arr[1], arr[0])

        # 日本語のデータ
    ld = open(trg_id_filename)
    lines = ld.readlines()
    ld.close()

    for line in lines:
        arr = line.split(" ")
        trg_ids[arr[1]] = trg_ids.get(arr[1], arr[0])

        # 確率のデータ
    ld = open(prob_data_filename)
    lines = ld.readlines()
    ld.close()

    for line in lines:
        arr = line.split(" ")
        key = arr[0]+" "+arr[1]
        prob_datas[key] = prob_datas.get(key, arr[2])

    # 入力文全文の単語をIDと対応させる
    for i in range(len(src_arr)):
        src_arr[i] = (src_ids[src_arr[i]], src_arr[i])

    # 重要エッジスコアを得るために、頻出度を数える
    for i in range(len(word_list)):
        for j in range(len(word_list[i])-1):
            name = (word_list[i][j], word_list[i][j+1])
            edge_sum[name] = edge_sum.get(name, 0) + 1

    # エッジの重み計算
    # {(("あああ", "いいいい"), (21, 22)), (("あああ", "いいいい"), (21, 22)}
    for u, v, d in graph.edges(data=True):
        # vの単語が原語から訳される最も高い確率を調べる
        # 単語対応確率スコアの計算 / 存在しない場合は0とする
        prob = 0.0
        for i in range(len(src_arr)):
            # 後ノードの日本語が辞書に存在するなら
            if v in trg_ids:
                key = trg_ids[v] +" "+ src_arr[i][0]
                # 日本語と英語の組み合わせが存在し、且つ、今までの確率より大きいなら
                if key in prob_datas:
                    #print v, src_arr[i][1], key, prob_datas[key]
                    #if prob_datas[key] > prob:
                    if round(float(prob)-float(prob_datas[key]), 10) < 0:
                        prob = prob_datas[key]

        # 重要エッジスコアの計算
        edge_score = float(edge_sum[(u,v)])/float(len(edge_sum))

        #重みの計算
        lamda = 0.5
        edge_weight = 1.0 - (lamda*edge_score + (1.0-lamda)*float(prob))
        d["weight"] = edge_weight

    #for u, v, d in graph.edges(data=True):
    #    print u, v, d
    return graph

def reranking(graph):
    word_graph = graph
    # 経路を全て取得し、短い順にソートする
    paths = sorted(nx.all_simple_paths(word_graph, source='start', target='end'), key=len)
    # 重みを計算してリランキング
    print "starting reranking....."
    datas = []
    for path in paths[:15]:
        weight = 0.0
        #print len(path)
        for i in range(len(path)-1):
            source, target = path[i], path[i+1]
            edge = word_graph[source][target]
            weight += edge['weight']
        datas.append((path, float(weight)/float(len(path))))
        #print('{}: {}'.format(path, float(weight)/float(len(path))))
    datas.sort(key=lambda tup: tup[1])
    return datas[0][0]

def update_accuracy(graph, list, sentence):
    #確率の高い3つのノード
    edges_weight = []
    edge_sum = {}
    src_id_filename = "./data/giza/trn.src.vcb"
    trg_id_filename = "./data/giza/trn.trg.vcb"
    prob_data_filename = "./data/giza/t3.final"
    word_list = list
    src_arr = sentence.split(" ")
    edge_list = {}
    src_ids = {}
    trg_ids = {}
    prob_datas = {}
    
    # データからidと単語をk-vで持つようにする
        # 原語のデータ
    ld = open(src_id_filename)
    lines = ld.readlines()
    ld.close()

    for line in lines:
        arr = line.split(" ")
        src_ids[arr[1]] = src_ids.get(arr[1], arr[0])

        # 日本語のデータ
    ld = open(trg_id_filename)
    lines = ld.readlines()
    ld.close()

    for line in lines:
        arr = line.split(" ")
        trg_ids[arr[1]] = trg_ids.get(arr[1], arr[0])

        # 確率のデータ
    ld = open(prob_data_filename)
    lines = ld.readlines()
    ld.close()

    for line in lines:
        arr = line.split(" ")
        key = arr[0]+" "+arr[1]
        prob_datas[key] = prob_datas.get(key, arr[2])

    # 入力文全文の単語をIDと対応させる
    for i in range(len(src_arr)):
        src_arr[i] = (src_ids[src_arr[i]], src_arr[i])

    # 与えられた文章と候補の日本語単語の確率の合計値を求める
    probs = {}
    for u, v, d in graph.edges(data=True):
        # vの単語が原語から訳される最も高い確率を調べる
        # 単語対応確率スコアの計算 / 存在しない場合は0とする
        prob = 0.0
        for i in range(len(src_arr)):
            # 後ノードの日本語が辞書に存在するなら
            if v in trg_ids:
                key = trg_ids[v] +" "+ src_arr[i][0]
                if key in prob_datas:
                    #print v, src_arr[i][1], key, prob_datas[key]
                    prob += float(prob_datas[key])
        probs[v] = probs.get(v, prob)

    probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
    #for i in range(len(probs)):
    #    print probs[i][0], probs[i][1]
    
    return probs[:3]


def tokenizer_alphabet(str):
    result = str.lower().replace(".", " .").replace(",", " ,").replace("'", " ' ").replace("!", " !")
    return result

def draw_graph(graph):
    nx.draw(graph)
    plt.show()


if __name__ == '__main__':
    #sentence = "I dreamed a excellent dream."
    #part_str = "I dreamed"
    lyrics = [
        ("I dreamed a excellent dream.", "I dreamed"),
        ("Soon you will die, And my memory will hide you!", "my memory"),
        ("Long as you live, I will still be here", "still be here"),
        ("It's over now I know inside No one must ever know", "It's over"),
        ("Do you think, That I'd ever set you free", "set you free"),
        ("Where does this feeling of power derive", "this feeling")
    ]

    result = []
    for i in range(len(lyrics)):
        grep_list = grep_corpus(lyrics[i][1])
        print "grep word list....."
        word_list = split_word(grep_list)
        print "create word list....."
        word_graph = create_word_graph(word_list, tokenizer_alphabet(lyrics[i][0]))
        print "create graph....."
        #翻訳精度をあげるために、強制的に通るノードを調べる
        #各単語の出現頻度を計算
        #出現頻度の高い上位25を含まないノードの検出
        #検出したノードと全文の単語対応確率を合計
        #確率の高い3つのノードを強制的に通過させる
        #prob_arr = update_accuracy(word_graph, word_list, tokenizer_alphabet(lyrics[i][0]))

        #for i in range(len(prob_arr)):
        #    print prob_arr[i][0], prob_arr[i][1]

        path = reranking(word_graph)
        result.append("".join(path[1:-1]))

    for i in range(len(result)):
        print result[i]
        #print "".join(path[i][1:-1])
        
        #draw_graph(word_graph)

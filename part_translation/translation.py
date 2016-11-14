#coding:utf-8
# 英文と部分的表現の2つを入力すると翻訳する
import MeCab
import jaconv
import networkx as nx
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
            #print line[:-1]

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
    
    # エッジの重みの取得
    edges_weight = calc_weight(word_list, sentence)
    print "calc weight....."

    # add edge
    for i in range(len(edges_weight)):
        graph.add_edge(edges_weight[i][0], edges_weight[i][1], weight=edges_weight[i][2])
    #print graph.edges(data=True)

    return graph

# return [(a, b, weight),(a, b, weight)]
def calc_weight(list, sentence):
    edges_weight = []
    edge_sum = {}
    src_id_filename = "./data/giza/116-11-14.011307.aynishim.trn.src.vcb"
    trg_id_filename = "./data/giza/116-11-14.011307.aynishim.trn.trg.vcb"
    prob_data_filename = "./data/giza/116-11-14.011307.aynishim.t3.final"
    src_arr = sentence.split(" ")
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

    # 入力文の単語をIDに変換
    for i in range(len(src_arr)):
        src_arr[i] = (src_ids[src_arr[i]], src_arr[i])
        
    #print src_arr

    for i in range(len(word_list)):
        word_list[i].insert(0, "start")
        word_list[i].append("end")
        for j in range(len(word_list[i])-1):
            # 重要エッジスコアを得るために、頻出度を数える
            name = word_list[i][j]+","+word_list[i][j+1]
            #print word_list[i][j]+","+word_list[i][j+1]
            edge_sum[name] = edge_sum.get(name, 0) + 1

    for k,v in edge_sum.items():
        arr = k.split(",")

        # j+1の単語が原語から訳される最も高い確率を調べる
        # 単語対応確率スコアの計算 / 存在しない場合は0とする
        prob = 0.0
        for i in range(len(src_arr)):
            # 後ノードの日本語が辞書に存在するなら
            if arr[1] in trg_ids:
                key = trg_ids[arr[1]] +" "+ src_arr[i][0]
                # 日本語と英語の組み合わせが存在し、且つ、今までの確率より大きいなら
                if key in prob_datas:
                    #if prob_datas[key] > prob:
                    if round(float(prob)-float(prob_datas[key]), 10) < 0:
                        print arr[1], src_arr[i][1]
                        prob = prob_datas[key]
                        #print key
                        #print prob

        # 重要エッジスコアの計算
        edge_score = float(v)/float(len(edge_sum))

        #重みの計算
        lamda = 0.5
        edge_weight = 1.0 - (lamda*edge_score + (1.0-lamda)*float(prob))
        edges_weight.append((arr[0], arr[1], edge_weight))
        
        #print edge_weight

    return edges_weight

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

def draw_graph(graph):
    nx.draw(graph)
    plt.show()


if __name__ == '__main__':
    #sentence = "I dreamed a excellent dream."
    #part_str = "I dreamed"
    num = 5
    lyrics = [
        ("I dreamed a excellent dream.", "I dreamed"),
        ("Soon you will die, And my memory will hide you!", "you will die"),
        ("Long as you live, I will still be here", "still be here"),
        ("It's over now I know inside No one must ever know", "It's over"),
        ("Do you think, That I'd ever set you free", "set you free"),
        ("Where does this feeling Of power derive", "this feeling")
    ]

    grep_list = grep_corpus(lyrics[num][1])
    print "grep word list....."
    word_list = split_word(grep_list)
    print "create word list....."
    word_graph = create_word_graph(word_list, lyrics[num][0])
    print "create graph....."
    path = reranking(word_graph)

    print "".join(path[1:-1])
    
    #draw_graph(word_graph)

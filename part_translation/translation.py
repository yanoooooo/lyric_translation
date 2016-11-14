#coding:utf-8
# 英文と部分的表現の2つを入力すると翻訳する
import MeCab
import jaconv
import networkx as nx
import matplotlib.pyplot as plt

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
        if score > 0.07:
            result.append(k)

    return result

# @param list array[][]
def create_word_graph(list):
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
    for i in range(len(word_list)):
        graph.add_nodes_from(word_list[i])
    
    # 重要エッジスコアの計算
    edges_weight = calc_weight(word_list)

    # add edge
    for i in range(len(edges_weight)):
        graph.add_edge(edges_weight[i][0], edges_weight[i][1], weight=edges_weight[2])
    print graph.edges(data=True)

    #for i in range(len(word_list)):
    #    for j in range(len(word_list[i])-1):
    #        graph.add_edge(word_list[i][j], word_list[i][j+1], weight=0.0)
            #print "("+word_list[i][j]+","+word_list[i][j+1]+")"
    #print graph.edges(data=True)

    return graph

# return [(a, b, weight),(a, b, weight)]
def calc_weight(list):
    edges_weight = []
    edge_sum = {}

    for i in range(len(word_list)):
        for j in range(len(word_list[i])-1):
            name = word_list[i][j]+","+word_list[i][j+1]
            edge_sum[name] = edge_sum.get(name, 0) + 1

    for k,v in edge_sum.items():
        arr = k.split(",")
        edges_weight.append((arr[0], arr[1], float(v)/float(len(edge_sum))))
        
        #print k, str(float(v)/float(len(edge_sum)))

    return edges_weight


def draw_graph(graph):
    nx.draw(graph)
    plt.show()


if __name__ == '__main__':
    sentence = "I dreamed a excellent dream."
    part_str = "I dreamed"
    grep_list = grep_corpus(part_str)
    word_list = split_word(grep_list)
    word_list[0].append("夢を")
    word_list[0].append("見たの")
    word_graph = create_word_graph(word_list)
    #draw_graph(word_graph)
    
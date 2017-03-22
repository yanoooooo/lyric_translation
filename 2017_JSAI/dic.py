#coding:utf-8
# 指定したコーパスから単語群を作成


def create_dictionary(filename, output):
    file = open(filename)
    data = file.read()
    file.close()
    words = tokens = data.split(" ")
    dic = {}
    for w in words:
        dic[w] = dic.get(w, 0) + 1

    file = open(output, "w")
    for k,v in dic.items():
        #file.write(k+","+str(v)+"\n")
        file.write(k.strip()+"\n")
    file.close()


if __name__ == '__main__':
    test = ['datas/test/corpus.txt', 'datas/test/dic.txt']
    piapro = ['datas/piapro/corpus.txt', 'datas/piapro/dic.txt']
    translate = ['datas/translate/corpus.txt', 'datas/translate/dic.txt']
    wiki = ['datas/wiki/corpus.txt', 'datas/wiki/dic.txt']

    datas = piapro
    create_dictionary(datas[0], datas[1])
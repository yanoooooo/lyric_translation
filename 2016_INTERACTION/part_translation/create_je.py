#coding:utf-8
#小説の対訳辞書から日本語と英語を抜き出して整形するプログラム

import sys
from lxml import etree
parser = etree.XMLParser(recover=True)

argvs = sys.argv

#引き数がない
if(len(argvs) < 2):
    print "you need args"
    sys.exit()

filename = argvs[1]

file_j = open("./org/"+filename[7:-5]+"_j.txt", "w")
file_e = open("./org/"+filename[7:-5]+"_e.txt", "w")

print filename

file = open(filename)
data = file.read()

#全文を読み込んで、パース
elem = etree.fromstring(data, parser=parser)


# 条件にマッチする要素をリストで返す
for e in elem.findall(".//T"):
    j = e.find(".//J").text.strip()
    e = e.find(".//E").text.strip()
    j = j.replace("\n", "")
    e = e.replace("\n", "")
    if bool(j and e):
        file_j.write(j.encode('utf-8')+"\n")
        file_e.write(e.encode('utf-8')+"\n")

file_j.close()
file_e.close()

file.close()
#coding:utf-8
#対応確率を見やすくするためのプログラム

src_id_filename = "./data/giza/116-11-14.011307.aynishim.trn.src.vcb"
trg_id_filename = "./data/giza/116-11-14.011307.aynishim.trn.trg.vcb"
prob_data_filename = "./data/giza/116-11-14.011307.aynishim.t3.final"
filename = "ttable_alt.txt"
src_ids = {}
trg_ids = {}
prob_datas = []

ld = open(src_id_filename)
lines = ld.readlines()
ld.close()

# 英語のデータ
for line in lines:
    arr = line.split(" ")
    src_ids[arr[0]] = src_ids.get(arr[0], arr[1])

# 日本語のデータ
ld = open(trg_id_filename)
lines = ld.readlines()
ld.close()

for line in lines:
    arr = line.split(" ")
    trg_ids[arr[0]] = trg_ids.get(arr[0], arr[1])

# 確率のデータ
ld = open(prob_data_filename)
lines = ld.readlines()
ld.close()

for line in lines:
    arr = line.split(" ")
    prob_datas.append((arr[0], arr[1], arr[2]))

#書き込み
file = open(filename, "w")

for i in range(len(prob_datas)):
    if prob_datas[i][0] != "0":
        if prob_datas[i][1] != "0":
            file.write(trg_ids[prob_datas[i][0]]+" "+src_ids[prob_datas[i][1]]+" "+prob_datas[i][2])

file.close()

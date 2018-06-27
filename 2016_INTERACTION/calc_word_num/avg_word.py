#coding:utf-8
# 読み込んだファイルの平均単語数を調べる

filenames_musical = ["musical/i_dreamed.txt", "musical/defying.txt", "musical/confrontation.txt"]
filenames_pops = []
filenames_jazz = []
filenames_children = ["children/hot_cross.txt", "children/itsy_bitsy.txt", "children/london.txt"]
filename = ["compression.txt"]

line_num = 0
word_num = 0

tune = 0

files = filename

for i in range(len(files)):
    file = open("data/"+files[i])
    lines = file.readlines()
    file.close()
    line_num = line_num + len(lines)
    for line in lines:
        if line == "\n":
            tune = tune+1
            continue
        word = line.split(" ")
        word_num = word_num + len(word)

print "全%s曲" % (tune+1)
print "単語数 %s, フレーズ数 %s" % (word_num, line_num)
print "平均単語数/フレーズ %s" % (float(word_num) / float(line_num-tune))



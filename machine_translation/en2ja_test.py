#coding:utf-8
from Translator import Translator

# 英日翻訳のテスト

en_lines = open('en-test.txt').read().split('\n')

epoch_num = 100
for epoch in range(epoch_num):
    model = Translator()
    modelfile = "./model/en2ja-" + str(epoch) + ".model"
    model.load_model(modelfile)
    for i in range(len(en_lines)-1):
        en_words = en_lines[i].lower().split()
        ja_words = model.test(en_words)
        print("{0}: {1}".format(epoch, ' '.join(ja_words))) 
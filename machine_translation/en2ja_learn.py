#coding:utf-8
from Translator import Translator
import time

# 英日翻訳の学習

start_time = time.time()
print("model new start.")

model = Translator(True)

elapsed_time = time.time() - start_time
print("model new finished. elapsed_time: {0:.1f}[sec]".format(elapsed_time))

epoch_num = 100
for epoch in range(epoch_num):
    start_time = time.time()
    print("{0} / {1} epoch start.".format(epoch + 1, epoch_num))

    # 学習を実施
    model.learn(True)
    modelfile = "./model/en2ja-" + str(epoch) + ".model"
    model.save_model(modelfile)

    elapsed_time = time.time() - start_time
    remaining_time = elapsed_time * (epoch_num - epoch - 1)
    print("{0} / {1} epoch finished.".format(epoch + 1, epoch_num), end="")
    print(" elapsed_time: {0:.1f}[sec]".format(elapsed_time), end="")
    print(" remaining_time: {0:.1f}[sec]".format(remaining_time))
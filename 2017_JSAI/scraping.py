#coding:utf-8
# ピアプロから歌詞を抜くスクリプト
# http://piapro.jp/text/?categoryId=7&page=2 :7がカテゴリ歌詞の模様
# http://piapro.jp/t/lDhP
# page = 5301まであり (2017/1/18) 30*5301 の歌詞

import lxml.html
import requests
import re
import time

max_page = 2 # max -> 5302
listname = "./datas/piapro/url_list.txt"
corpusname = "./datas/piapro/corpus.txt"

# ------------------------ URLリスト ------------------------
def create_url_list():
    target_url = "http://piapro.jp/text/?categoryId=7&page="
    

    lyrics_url_list = []

    for num in range(1, max_page):
        print target_url+str(num)
        target_html = requests.get(target_url+str(num)).text
        root = lxml.html.fromstring(target_html)
        #aタグの内容を全て取得
        p = re.compile('^\/t\/.{4}')
        for a in root.xpath('//a'):
            if p.match(a.get('href')):
                lyrics_url_list.append(a.get('href').strip())
                #print(a.get('href'))
        time.sleep(2)

    # 重複削除
    lyrics_url_list = set(lyrics_url_list)
    #lyrics_url_list = ["/t/Ji9i", "/t/cWJp"]

    # 歌詞URLリスト作成
    file = open(listname, "w")
    for a in lyrics_url_list:
        #print a
        file.write(a+"\n")
    file.close()

# ------------------------ 歌詞作成 ------------------------
def create_lyrics_corpus():
    file = open(listname)
    lines = file.readlines()
    file.close()

    file = open(corpusname, "w")
    print("歌曲数: %d 曲") % len(lines)
    for a in lines:
        print a.strip()
        target_url = "http://piapro.jp" + a.strip()
        target_html = requests.get(target_url).text
        root = lxml.html.fromstring(target_html)
        
        file.write(root.cssselect('#_txt_main')[0].text_content().encode("utf-8")+"\n")
        #print root.cssselect('#_txt_main')[0].text_content()
        time.sleep(2)
    file.close()


if __name__ == '__main__':
    create_url_list()
    create_lyrics_corpus()

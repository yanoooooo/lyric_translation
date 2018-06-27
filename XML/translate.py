#coding:utf-8
import re
from microsofttranslator import Translator
from xml.etree import ElementTree
from auth import AzureAuthClient
import requests

"""
# 渡された配列の原言語の歌詞を日本語に翻訳する
@param  array [(mora_num, "lyrics"), (mora_num, "lyrics").....]
@return array [(mora_num, "lyrics", "歌詞"), (mora_num, "lyrics", "歌詞").....]
"""
def translate(mora_src):
    result = []

    # アプリケーション名とキーの設定
    client_secret = '0cad3399b0214a31acafe914d6cac203'
    auth_client = AzureAuthClient(client_secret)
    bearer_token = 'Bearer ' + auth_client.get_access_token()

    headers = {"Authorization ": bearer_token}
    
    for ms in mora_src:
        # Call to Microsoft Translator Service
        translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&to={}".format(ms[1], "ja")
        translationData = requests.get(translateUrl, headers = headers)
        # parse xml return values
        translation = ElementTree.fromstring(translationData.text.encode('utf-8'))
        obj_ln = translation.text

        obj_ln = obj_ln.encode('utf-8')
        obj_ln = obj_ln.replace("。", "")
        obj_ln = obj_ln.replace("・", "")
        # 英語が残ってしまった場合は削除
        obj_ln = re.sub(r'[a-zA-Z]+', "", obj_ln)
        print(obj_ln)
        result.append((ms[0], ms[1], obj_ln))
    
    return result

if __name__ == "__main__":
    text = [{3,"The itsy bitsy spider went up the water spout."}]
    translate(text)
#coding:utf-8
from microsofttranslator import Translator

"""
# 渡された配列の原言語の歌詞を日本語に翻訳する
@param  array [(mora_num, "lyrics"), (mora_num, "lyrics").....]
@return array [(mora_num, "lyrics", "歌詞"), (mora_num, "lyrics", "歌詞").....]
"""
def translate(mora_src):
    result = []
    # アプリケーション名とキーの設定
    #translator = Translator('TranslateAppOnRS', 'KiRTM60FqU2CLMDrQhVdd3yeicWSztHtLiDx5JRIavA=')
    translator = Translator('score_translation', 'AnG5Mp3zZZHWk3qjuvI5nt0jVBuwJrrPi6SUpmPhFV0=')

    for ms in mora_src:
        obj_ln = translator.translate(ms[1], "ja")
        result.append((ms[0], ms[1], obj_ln))

    return result
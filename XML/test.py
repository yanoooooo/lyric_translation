"""
Example application showing the use of the Translate method in the Text Translation API.
"""

from xml.etree import ElementTree
from auth import AzureAuthClient
import requests

doItAgain = "yes"

def GetTextAndTranslate(finalToken):

    fromLangCode = " "
    toLangCode = " "
    textToTranslate = " "

    print " "
    print "   Language List"
    print "     English"
    print "     German"
    print "     Italian"
    print "     Spanish"
    print "     French"

    # Get the source language
    while (fromLangCode == " "):
        sourceLang = raw_input("Type the name of a language from the list that you want to translate from: ")

        if (sourceLang == "english") or (sourceLang == "English"):
            fromLangCode = "en"
        elif (sourceLang == "German") or (sourceLang == "german"):
            fromLangCode = "de"
        elif (sourceLang == "Italian") or (sourceLang == "italian"):
            fromLangCode = "it"
        elif (sourceLang == "Spanish") or (sourceLang == "spanish"):
            fromLangCode = "es"
        elif (sourceLang == "French") or (sourceLang == "french"):
            fromLangCode = "fr"
        else:
            print " "
            print "You need to pick a language from the List"

            raw_input("Press any key to continue")

    print " "

    # Get the destination language
    while (toLangCode == " "):
        destLang = raw_input("Type the name of a language from the list that you want to translate to: ")

        if (destLang == "english") or (destLang == "English"):
            toLangCode = "en"
        elif (destLang == "German") or (destLang == "german"):
            toLangCode = "de"
        elif (destLang == "Italian") or (destLang == "italian"):
            toLangCode = "it"
        elif (destLang == "Spanish") or (destLang == "spanish"):
            toLangCode = "es"
        elif (destLang == "French") or (destLang == "french"):
            toLangCode = "fr"
        else:
            print " "
            print "You need to pick a language from the List"

            raw_input("Press any key to continue")

    print " "

    textToTranslate = raw_input("Type the text that you want to translate:  ")

    print " "

    # Call to Microsoft Translator Service
    headers = {"Authorization ": finalToken}
    translateUrl = "http://api.microsofttranslator.com/v2/Http.svc/Translate?text={}&to={}".format(textToTranslate, toLangCode)

    translationData = requests.get(translateUrl, headers = headers)
    # parse xml return values
    translation = ElementTree.fromstring(translationData.text.encode('utf-8'))
    # display translation
    print "The translation is---> ", translation.text

    print " "


if __name__ == "__main__":

    client_secret = '0cad3399b0214a31acafe914d6cac203'
    auth_client = AzureAuthClient(client_secret)
    bearer_token = 'Bearer ' + auth_client.get_access_token()

    while (doItAgain == 'yes') or (doItAgain == 'Yes'):
        GetTextAndTranslate(bearer_token)
        print ' '
        doItAgain = raw_input('Type yes to translate more, any other key to end: ')

    goodBye = raw_input('Thank you for using Microsoft Translator, we appreciate it. Good Bye')
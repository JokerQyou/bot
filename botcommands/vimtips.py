# coding: utf-8
import requests

def vimtips(msg):
    try:
        tip = requests.get('http://vim-tips.com/random_tips/json').json()
    except Exception as e:
        return None
    return u'%s\n%s' % (tip['Content'], tip['Comment'], )

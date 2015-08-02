# coding: utf-8
import config
from config import __bot__


def start(msg=None, debug=False):
    '''显示欢迎语'''
    about_text = (u'你好，我是 %s，蠢萌的机器人酱 O(∩_∩)O~~\n'
                  u'主人是 @%s，同时也听 %s 的话 (●\'v\'●)ﾉ♥\n'
                  u'戳这里→ https://github.com/JokerQyou/bot ←看我的档案')
    owner = config.get('owner')
    admins = list(config.get('admins'))
    admins_striped = list(set(admins + [owner]))
    admins_striped.remove(owner)
    admins_striped = u'、'.join(admins_striped)
    return about_text % (__bot__, owner, admins_striped, )

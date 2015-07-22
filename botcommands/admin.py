# coding: utf-8
import config
from config import require_admin
from utils import extract_texts


@require_admin
def listadmin(msg=None, debug=False):
    ''' List admins '''
    return u'当前的管理员：\n%s' % u'\n'.join(config.get('admins'))


@require_admin
def addadmin(msg=None, debug=False):
    ''' Add a user as admin '''
    command, options, words = extract_texts(msg['text'])
    if not words:
        return u'你想添加谁为管理员？'
    admins = config.get('admins')
    for _admin in words[1:]:
        admins.append(_admin)

    return u'添加了 %d 位管理员：\n%s' % (len(words[1:]), u'、'.join(words[1:]), )


@require_admin
def deladmin(msg=None, debug=False):
    ''' Delete an admin (cannot delete self) '''
    admins = config.get('admins')
    command, options, words = extract_texts(msg['text'])
    non_admins, removed = [], []
    if not words:
        return u'你想删除谁的管理员权限？'
    for _admin in words:
        if _admin not in admins:
            non_admins.append(_admin)
        else:
            admins.remove(_admin)
            removed.append(_admin)

    if removed:
        response = u'移除了这些管理员：%s' % u'、'.join(removed)
    if non_admins:
        response += u'\n你想删除的 %s 还不是管理员' % u'、'.join(non_admins)

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
        return u'拜托，你想添加谁为管理员？一次性说完啦！'
    admins = config.get('admins')
    added = []
    for _admin in words:
        if _admin not in admins:
            admins.append(_admin)
            added.append(_admin)

    return u'添加了 %d 位管理员：\n%s' % (len(added), u'、'.join(added), )


@require_admin
def deladmin(msg=None, debug=False):
    ''' Delete an admin (cannot delete self) '''
    admins = config.get('admins')
    command, options, words = extract_texts(msg['text'])
    non_admins, removed = [], []
    failed = []
    response = u''
    if not words:
        return u'拜托，你想删除谁的管理员权限？一次性说完啦！'
    for _admin in words:
        if _admin == msg['from']['username']:
            failed.append(_admin)
            continue
        if _admin not in admins:
            non_admins.append(_admin)
        else:
            admins.remove(_admin)
            removed.append(_admin)

    if removed:
        response = u'移除了这些管理员：%s' % u'、'.join(removed)
    if non_admins:
        response += u'\n你想删除的 %s 还不是管理员' % u'、'.join(non_admins)
    if failed:
        response += u'\n这些管理员不能被你删除：%s' % u'、'.join(failed)

    return response

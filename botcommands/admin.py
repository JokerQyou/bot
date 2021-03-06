# coding: utf-8
import config
from config import require_admin
from utils import extract_texts


@require_admin
def listadmin(msg=None, debug=False):
    '''（管理员）列出管理员'''
    return u'当前的管理员：\n%s' % u'\n'.join(config.get('admins'))


@require_admin
def addadmin(msg=None, debug=False):
    '''（管理员）添加管理员'''
    command, options, words = extract_texts(msg.text)
    if not words:
        return u'拜托，你想添加谁为管理员？一次性说完啦！'
    admins = config.get('admins')
    added = []
    for person in words:
        _admin = person if person.startswith('@') else '@%s' % person
        if _admin not in admins:
            admins.append(_admin)
            added.append(_admin)

    return u'添加了 %d 位管理员：\n%s' % (len(added), u'、'.join(added), )


@require_admin
def deladmin(msg=None, debug=False):
    '''（管理员）删除管理员'''
    admins = config.get('admins')
    command, options, words = extract_texts(msg.text)
    non_admins, removed = [], []
    failed = []
    response = u''
    if not words:
        return u'拜托，你想删除谁的管理员权限？一次性说完啦！'
    for person in words:
        _admin = person if person.startswith('@') else '@%s' % person
        # Cannot delete self
        if _admin == msg.from_user.name:
            failed.append(_admin)
            continue
        # Cannot delete owner
        if _admin == config.get('owner'):
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

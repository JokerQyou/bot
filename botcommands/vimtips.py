# coding: utf-8
from random import randint

import requests
from redis_wrap import get_hash, SYSTEMS
from rq.decorators import job

from config import require_admin
from utils import extract_texts


def vimtips(msg=None, debug=False):
    '''显示一条 vim 使用技巧'''
    try:
        existing_tips = get_hash('vimtips')
        _len = len(existing_tips)
        if _len > 0:
            _index = randint(0, _len - 1)
            _k = existing_tips.keys()[_index]
            _v = existing_tips[_k]
            tip = {
                'Content': _k,
                'Comment': _v
            }
        else:
            tip = requests.get('http://vim-tips.com/random_tips/json').json()
            existing_tips.update({
                tip['Content']: tip['Comment']
            })
        collect_tip.delay()
    except Exception as e:
        print e
        return '哦，不小心玩坏了……'
    result = '%s\n%s' % (tip['Content'], tip['Comment'], )
    if debug:
        result = '%s\n%s' % (result, ('debug: 当前有 %d 条 vimtips' % _len), )
    return result


@require_admin
def addvimtip(msg=None, debug=False):
    '''（管理员）添加一条 vim 使用技巧'''
    usage = '命令格式：\n/addvimtip [/forceadd]\n内容\n解释'
    if msg.text is None:
        return usage
    command, options, words = extract_texts(msg.text)
    if not words:
        return usage
    force_add = '/forceadd' in options
    # We do not want words here, we want lines
    parts = [i.strip() for i in msg.text.strip().split('\n')]
    if len(parts) < 3 or not all([bool(i) for i in parts]):
        return usage

    content, comment = parts[1], parts[2]
    tips = get_hash('vimtips')
    if content in tips:
        if not force_add:
            return '这条 tip 已经存在了，希望覆盖的话可以使用 /forceadd 选项'
    tips.update({
        content: comment
    })
    return u'添加了一条 vimtip：\n%s\n%s' % (content, comment, )


# Fetch a new tip in RQ queue
@job('default', connection=SYSTEMS['default'], result_ttl=5)
def collect_tip():
    tip = requests.get('http://vim-tips.com/random_tips/json').json()
    get_hash('vimtips').update({
        tip['Content']: tip['Comment']
    })

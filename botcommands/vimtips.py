# coding: utf-8
from random import randint

import requests
from redis_wrap import get_hash, SYSTEMS
from rq.decorators import job

from config import require_admin

def vimtips(msg=None, debug=False):
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
        return '哦，不小心玩坏了……'
    result = '%s\n%s' % (tip['Content'], tip['Comment'], )
    if debug:
        result = '%s\n%s' % (result, ('debug: 当前有 %d 条 vimtips' % _len), )
    return result

@require_admin
def addvimtip(msg=None, debug=False):
    usage = '格式：\n/addvimtip\n内容\n解释'
    if not msg or not msg.get('text'):
        return usage
    parts = [i.strip() for i in msg.get('text').strip().split('\n')]
    if len(parts) < 3 or not all([bool(i) for i in parts]):
        return usage

    force_add = '/forceadd' in parts
    content, comment = parts[1], parts[2]
    tips = get_hash('vimtips')
    if content in tips.keys():
        if not force_add:
            return '这条 tip 已经存在了，希望覆盖的话可以使用 /forceadd 选项覆盖'
    tips.update({
        content: comment
    })
    return '添加了一条 vimtip：\n%s\n%s' % (content, comment, )

# Fetch a new tip in RQ queue
@job('default', connection=SYSTEMS['default'], result_ttl=5)
def collect_tip():
    tip = requests.get('http://vim-tips.com/random_tips/json').json()
    get_hash('vimtips').update({
        tip['Content']: tip['Comment']
    })

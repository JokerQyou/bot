# coding: utf-8
import json
from redis_wrap import get_hash, get_list

__config__ = 'config.json'

with open(__config__, 'r') as cfr:
    config = json.loads(cfr.read())

PATH = '/%s' % '/'.join(config.get('server').replace('https://', '').replace('http://', '').split('/')[1:])

TOKEN = config.get('token')
SERVER = config.get('server')
PORT = config.get('port')

def get(key):
    ''' Get raw config from redis with a prefix '''
    list_keys = ('admins', )
    hash_keys = (None, )
    real_key = '%s:%s' % (str(__name__), key, )
    if key in list_keys:
        return get_list(real_key)
    elif key in hash_keys:
        return get_hash(real_key)

def init_redis():
    admins = get('admins')
    if len(admins) == 0:
        [admins.append(admin) for admin in config.get('admins')]

def require_admin(func):
    def wrapper(**kwargs):
        msg = kwargs.get('msg', None)
        if not msg:
            return ''
        if msg['from']['username'] not in get('admins'):
            return u'这个功能只有管理员可以使用'
        return func(**kwargs)
    return wrapper

init_redis()

# coding: utf-8
from os import path
import json

from redis_wrap import get_hash, get_list, SYSTEMS

__name__ = 'eth0_bot'
__bot__ = 'eth0'
__config__ = path.abspath(path.join(path.dirname(__file__), 'config.json'))

with open(__config__, 'r') as cfr:
    config = json.loads(cfr.read())

PATH = '/%s' % '/'.join(
    config['server'].replace('https://', '')
    .replace('http://', '').split('/')[1:]
)

TOKEN = config.get('token')
SERVER = config.get('server')
PORT = config.get('port')

redis = SYSTEMS['default']


def get(key, default=None):
    ''' Get raw config from redis with a prefix '''
    list_keys = ('admins', )
    hash_keys = (None, )
    string_keys = ('owner', )
    real_key = '%s:%s' % (str(__name__), key, )
    if key in list_keys:
        return get_list(real_key)
    elif key in hash_keys:
        return get_hash(real_key)
    elif key in string_keys:
        r = redis.get(key)
        if r is None:
            r = default
        return r


def set(key, value):
    string_keys = ('owner', )
    if key in string_keys:
        redis.set(key, value)


def init_redis():
    admins = get('admins')
    owner = get('owner')
    if len(admins) == 0:
        [admins.append(admin) for admin in config.get('admins')]
    if owner != config.get('owner'):
        set('owner', config.get('owner'))


def require_admin(func):
    def wrapper(*args, **kwargs):
        msg = kwargs.get('msg', None) if len(args) == 0 else args[0]
        if not msg:
            return ''
        if msg['from']['username'] not in get('admins'):
            return u'这个功能只有管理员可以使用'
        return func(*args, **kwargs)
    return wrapper

init_redis()

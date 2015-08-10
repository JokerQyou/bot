# coding: utf-8
from functools import wraps
from os import path
import json

import certifi
from redis_wrap import get_hash, get_list, SYSTEMS
import paho.mqtt.publish as publish

__name__ = 'eth0_bot'
__bot__ = 'eth0'
__config__ = path.abspath(path.join(path.dirname(__file__), 'config.json'))

with open(__config__, 'r') as cfr:
    config = json.loads(cfr.read())

PATH = '/%s' % '/'.join(
    config['server'].replace('https://', '')
    .replace('http://', '').split('/')[1:]
)

for k in config.keys():
    if isinstance(config[k], (str, unicode, )):
        template = '%s="%s"'
    else:
        template = '%s=%s'
    exec(template % (k.upper(), config[k]))

redis = SYSTEMS['default']


def get(key, default=None):
    ''' Get raw config from redis with a prefix '''
    list_keys = ('admins', )
    hash_keys = ('conversations', )
    string_keys = ('owner', 'last_update_id', )
    real_key = '%s:%s' % (str(__name__), key, )
    if key in list_keys:
        return get_list(real_key)
    elif key in hash_keys:
        return get_hash(real_key)
    elif key in string_keys:
        r = redis.get(real_key)
        if r is None:
            r = default
        return r


def set(key, value):
    string_keys = ('owner', 'last_update_id', )
    if key in string_keys:
        key = '%s:%s' % (str(__name__), key, )
        redis.set(key, value)


def init_redis():
    admins = get('admins')
    owner = get('owner')
    c_owner = config.get('owner')
    c_owner = c_owner if c_owner.startswith('@') else '@%s' % c_owner
    if len(admins) == 0:
        [admins.append(admin if admin.startswith('@') else '@%s' % admin)
            for admin in config.get('admins')]
    if owner != c_owner:
        set('owner', c_owner)


def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        msg = kwargs.get('msg', None) if len(args) == 0 else args[0]
        if not msg:
            return ''
        if msg.from_user.name not in get('admins'):
            return u'这个功能只有管理员可以使用'
        return func(*args, **kwargs)
    return wrapper


def pi_command(func):
    global MQTT
    @wraps(func)
    def wrapper(msg=None, debug=False):
        return publish.single(
            MQTT['topic'], payload=json.dumps(msg),
            qos=MQTT['qos'], hostname=MQTT['host'],
            port=MQTT['port'], client_id='%s:client' % __name__,
            keepalive=60, tls={'ca_certs': certifi.where()},
            auth={'username': MQTT['username'], 'password': MQTT['password']}
        )
    return wrapper


init_redis()

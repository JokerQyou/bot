# coding: utf-8
import json

import flask
from flask import request
import redis
from redis_wrap import get_hash, get_list
import telegram

__name__ = u'eth0_bot'
__author__ = u'Joker_Qyou'
__config__ = u'config.json'

app = flask.Flask(__name__)
app.debug = False

with open(__config__, 'r') as cfr:
    config = json.loads(cfr.read())

path = '/%s' % '/'.join(config.get('server').replace('https://', '').replace('http://', '').split('/')[1:])

raw_redis = redis.StrictRedis(**config.get('redis'))

def init_redis():
    admins = get_list('admins')
    if not admins:
        [admins.append(admin) for admin in config.get('admins')]

init_redis()

@app.route('%s/%s' % (path, config.get('token').split(':')[-1], ), methods=('POST', ))
def webhook():
    ''' WebHook API func '''
    update = request.json
    handle_message(update.get('message'))
    return ''

def handle_message(message):
    text = message.get('text', '').strip()
    photo = message.get('photo', {})
    if text:
        if text.startswith('/'):
            handle_command(text, message)
        else:
            handle_text(text, message)
    if photo:
        send_reply(text='很好，我收到了一张图片，然而这并没有什么卯用', message=message)

def handle_command(text, message):
    text = 'You used %s command' % text
    bot.sendMessage(text=text, chat_id=message.get('chat').get('id'))

def handle_text(text, message):
    text = '%s: %s' % ('复读机', text, )
    bot.sendMessage(text=text, chat_id=message.get('chat').get('id'))

def send_reply(text=None, photo=None, emoji=None, audio=None, message=None):
    if not message:
        raise RuntimeError('Dont know the chat id')
    if not text: return
    bot.sendMessage(text=text, chat_id=message.get('chat').get('id'))

bot = telegram.Bot(token=config.get('token'))
bot.setWebhook('%s/%s' % (config.get('server'), config.get('token').split(':')[-1], ))

app.run(host='0.0.0.0', port=config.get('port'))


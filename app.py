# coding: utf-8
import json

import flask
from flask import request
import redis
from redis_wrap import get_hash, get_list
import telegram

from utils import *
import botcommands

__name__ = u'eth0_bot'
__author__ = u'Joker_Qyou'
__config__ = u'config.json'

app = flask.Flask(__name__)
app.debug = True

with open(__config__, 'r') as cfr:
    config = json.loads(cfr.read())

path = '/%s' % '/'.join(config.get('server').replace('https://', '').replace('http://', '').split('/')[1:])

raw_redis = redis.StrictRedis(**config.get('redis'))

def init_redis():
    admins = get_list('admins')
    if len(admins) == 0:
        [admins.append(admin) for admin in config.get('admins')]

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
        send_reply(text='很好，我收到了一张图片，然而这并没有什么卯月', message=message)

def handle_command(text, message):
    text = text[1:]
    if hasattr(botcommands, text):
        result = getattr(botcommands, text)(message)
        return send_reply(text=result, message=message)
    text = u'%s 命令现在并没有什么卯月' % text
    send_reply(text=text, message=message)

def handle_text(text, message):
    text = u'%s: %s' % (u'复读机', text, )
    send_reply(text=text, message=message)

def send_reply(text=None, photo=None, emoji=None, audio=None, message=None, reply=True):
    if not message:
        raise RuntimeError('Dont know the chat id')
    if not text: return
    bot.sendMessage(text=smart_text(text), 
                    chat_id=message.get('chat').get('id'), 
                    reply_to_message_id=message.get('id'))

def main():
    init_redis()

    bot = telegram.Bot(token=config.get('token'))
    bot.setWebhook('%s/%s' % (config.get('server'), config.get('token').split(':')[-1], ))

    app.run(host='0.0.0.0', port=config.get('port'))

if __name__ == '__main__':
    main()

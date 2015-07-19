# coding: utf-8
import json

import flask
from flask import request
import redis
import telegram

import config
from utils import *
import botcommands

__name__ = 'eth0_bot'
__author__ = 'Joker_Qyou'

app = flask.Flask(__name__)
app.debug = True

bot = telegram.Bot(token=config.TOKEN)
bot.setWebhook('%s/%s' % (config.SERVER, config.TOKEN.split(':')[-1], ))

@app.route('%s/%s' % (config.PATH, config.TOKEN.split(':')[-1], ), methods=('POST', ))
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

def handle_command(text, message, debug=False):
    if '/debug' in text and message['from']['username'] in config.get('admins'):
        debug = True
    texts = text.split(' ')
    command = texts[0][1:]
    if hasattr(botcommands, command):
        result = getattr(botcommands, command)(message, debug=debug)
        return send_reply(text=result, message=message)
    text = u'%s 命令现在并没有什么卯月' % command
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
    app.run(host='0.0.0.0', port=config.PORT)

if __name__ in ('__main__', u'eth0_bot', ):
    main()

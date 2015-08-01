# coding: utf-8
import json

import flask
from flask import request
from rq.decorators import job
from redis_wrap import SYSTEMS
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


@app.route('%s/%s' % (config.PATH, config.TOKEN.split(':')[-1], ),
           methods=('POST', ))
def webhook():
    ''' WebHook API func '''
    update = request.json
    if app.debug:
        print json.dumps(update, indent=4)
    handle_message(update.get('message'))
    return ''


def handle_message(message):
    text = message.get('text', '').strip()
    # photo = message.get('photo', {})
    if text:
        if text.startswith('/'):
            handle_command(text, message)
        else:
            handle_text(text, message)
    # if photo:
    #     send_reply(text='很好，我收到了一张图片，然而这并没有什么卯月', message=message)


@job('reply', connection=SYSTEMS['default'], result_ttl=5)
def handle_command(text, message, debug=False):
    if '/debug' in text \
            and message['from']['username'] in config.get('admins'):
        debug = True
    command, options, words = extract_texts(message.get('text'))
    if not smart_text(command).isalnum():
        return send_reply(text='机器人酱并不懂你发的那是什么玩意', message=message)
    if command == 'ls':
        return send_reply(text=list_commands(message, debug=debug),
                          message=message)
    if hasattr(botcommands, command):
        result = getattr(botcommands, command)(message, debug=debug)
        return send_reply(text=result, message=message)
    if debug:
        text = u'%s 命令现在并没有什么卯月' % command
        send_reply(text=text, message=message)


@config.require_admin
def list_commands(msg, debug=False):
    '''List all commands available'''
    commands = []
    for command in dir(botcommands):
        attr = getattr(botcommands, command)
        if callable(attr):
            commands.append('%s - %s\n' % (command, attr.func_doc, ))
    return ''.join(commands)


def handle_text(text, message):
    text = u'%s: %s' % (u'复读机', text, )
    # send_reply(text=text, message=message)


def send_reply(text=None, photo=None, emoji=None,
               audio=None, video=None, fileobj=None,
               location=None, message=None, reply=True):
    if not message:
        raise RuntimeError('Dont know the chat id')
    # Currently text reply is the only supported type
    if not text:
        return
    action = 'typing'
    if photo:
        action = 'upload_photo'
    elif audio:
        action = 'upload_audio'
    elif video:
        action = 'upload_video'
    elif fileobj:
        action = 'upload_document'
    elif location:
        action = 'find_location'
    bot.sendChatAction(chat_id=message.get('chat').get('id'),
                       action=action)
    bot.sendMessage(text=smart_text(text),
                    chat_id=message.get('chat').get('id'),
                    reply_to_message_id=message.get('message_id'))


def main():
    app.run(host='0.0.0.0', port=config.PORT)

if __name__ in ('__main__', u'eth0_bot', ):
    main()

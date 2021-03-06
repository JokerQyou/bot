# coding: utf-8
import json

import telegram
from rq.decorators import job
from redis_wrap import SYSTEMS

import config
import botcommands
from utils import *

bot = None


@job('reply', connection=SYSTEMS['default'], result_ttl=5)
def handle_update(update, telegram_bot=None):
    global bot
    if telegram_bot is None:
        print 'no bot'
        bot = telegram.Bot(token=config.TOKEN)
    else:
        bot = telegram_bot

    message = update.message
    # Save conversation info
    conversations = config.get('conversations')
    str_chat_id = smart_text(message.chat_id)
    if message.left_chat_participant is not None:
        if smart_text(
            message.left_chat_participant.name[1:]
        ) == config.__name__:
            del conversations[str_chat_id]
            return
    # Store chat info if it does not exist
    if str_chat_id not in conversations:
        if isinstance(message.chat, (telegram.User, )):
            conversations[str_chat_id] = message.chat.name
        elif isinstance(message.chat, (telegram.GroupChat, )):
            conversations[str_chat_id] = message.chat.title
    else:
        # Update chat info if it changed
        if isinstance(message.chat, (telegram.User, ))\
                and smart_text(
                    message.chat.name
                ) != smart_text(conversations[str_chat_id]):
            conversations[str_chat_id] = message.chat.name
        elif isinstance(message.chat, (telegram.GroupChat, ))\
                and smart_text(
                    message.chat.title
                ) != smart_text(conversations[str_chat_id]):
            conversations[str_chat_id] = message.chat.title

    if message.text:
        text = message.text.strip()
        if text.startswith('/'):
            handle_command(text, message)
        else:
            handle_text(text, message)
    elif message.photo:
        pass
    elif message.video:
        pass
    elif message.document:
        pass
    elif message.audio:
        pass
    elif message.location:
        pass


def handle_command(text, message, debug=False):
    # Admins can toggle debug mode for commands
    if '/debug' in text \
            and message.from_user.name in config.get('admins'):
        debug = True
    if '@' in text and config.__name__ not in text.split('@'):
        return
    command, options, words = extract_texts(message.text)
    if not smart_text(command).isalnum():
        return send_reply(text='机器人酱并不懂你发的那是什么玩意', message=message)
    if command in ('ls', 'help', ):
        return send_reply(text=list_commands(message, debug=debug),
                          message=message)
    if hasattr(botcommands, command):
        result = getattr(botcommands, command)(message, debug=debug)
        if result is not None:
            return send_reply(text=result, message=message)
    if debug:
        text = u'%s 命令现在并没有什么卯月' % command
        send_reply(text=text, message=message)


@job('reply', connection=SYSTEMS['default'], result_ttl=5)
def handle_pi_command(msg_payload, telegram_bot=None):
    global bot
    if telegram_bot is None:
        bot = telegram.Bot(token=config.TOKEN)
    else:
        bot = telegram_bot
    try:
        msg = json.loads(msg_payload)
        reply_to = telegram.Message.de_json(msg['reply_to'])
        return send_reply(text=msg.get('text', None),
                          photo=msg.get('photo', None),
                          emoji=msg.get('emoji', None),
                          audio=msg.get('audio', None),
                          video=msg.get('video', None),
                          location=msg.get('location', None),
                          message=reply_to)
    except Exception:
        try:
            return send_plain_text(
                text=msg.get('text', None),
                photo=msg.get('photo', None),
                message=reply_to
            )
        except Exception:
            print extract_traceback()


def list_commands(msg, debug=False):
    '''List all commands available'''
    commands = []
    for command in dir(botcommands):
        attr = getattr(botcommands, command)
        if callable(attr):
            commands.append('%s - %s\n' % (command, attr.func_doc, ))
    commands.append('help - 列出所有可用的命令')
    return ''.join(commands)


def handle_text(text, message):
    text = u'%s: %s' % (u'复读机', text, )
    # send_reply(text=text, message=message)


def send_plain_text(text=None, photo=None, message=None, reply=True):
    if photo and 'http' in photo:
        content = photo
    elif text:
        content = text
    bot.sendChatAction(chat_id=message.chat_id,
                       action='typing')
    bot.sendMessage(message.chat_id,
                    smart_text(content),
                    reply_to_message_id=message.message_id)


def send_reply(text=None, photo=None, emoji=None,
               audio=None, video=None, fileobj=None,
               location=None, message=None, reply=True):
    if not message:
        raise RuntimeError('Dont know the chat id')
    # Currently text reply is the only supported type
    action = 'typing'
    if photo:
        action = 'upload_photo'
        bot.sendChatAction(chat_id=message.chat_id,
                           action=action)
        bot.sendPhoto(message.chat_id,
                      photo,
                      reply_to_message_id=message.message_id)
        return
    elif audio:
        action = 'upload_audio'
    elif video:
        action = 'upload_video'
    elif fileobj:
        action = 'upload_document'
    elif location:
        action = 'find_location'
    bot.sendChatAction(chat_id=message.chat_id,
                       action=action)
    bot.sendMessage(message.chat_id,
                    smart_text(text),
                    reply_to_message_id=message.message_id)

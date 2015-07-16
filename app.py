# coding: utf-8
import json

import flask
from flask import request
import telegram

__name__ = u'eth0_bot'
__author__ = u'Joker_Qyou'
__config__ = u'config.json'

app = flask.Flask(__name__)
app.debug = False

with open(__config__, 'r') as cfr:
    config = json.loads(cfr.read())

path = '/%s' % '/'.join(config.get('server').replace('https://', '').replace('http://', '').split('/')[1:])

@app.route(u'%s/%s' % (path, config.get('token').split(':')[-1], ), methods=('POST', ))
def webhook():
    ''' WebHook API func '''
    update = request.json
    bot.sendMessage(chat_id=update.get('message').get('chat').get('id'), text=json.dumps(update, indent=4))
    return ''

bot = telegram.Bot(token=config.get('token'))
bot.setWebhook(u'%s/%s' % (config.get('server'), config.get('token').split(':')[-1], ))

app.run(host='0.0.0.0', port=config.get('port'))


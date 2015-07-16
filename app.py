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

bot = telegram.Bot(token=token_info)
bot.setWebhook(u'%(server)s/%(token)s' % config)

@app.route(u'/%s' % config.get('token').split(':')[-1])
def webhook():
    ''' WebHook API func '''
    print request.POST


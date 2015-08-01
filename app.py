# coding: utf-8
import json

import flask
from flask import request
import telegram

import config
import operations

__bot_name__ = 'eth0_bot'
__author__ = 'Joker_Qyou'

app = flask.Flask(__name__)
app.debug = config.DEBUG

bot = telegram.Bot(token=config.TOKEN)
bot.setWebhook('%s/%s' % (config.SERVER, config.TOKEN.split(':')[-1], ))


@app.route('%s/%s' % (config.PATH, config.TOKEN.split(':')[-1], ),
           methods=('POST', ))
def webhook():
    ''' WebHook API func '''
    update = request.json
    if app.debug:
        print json.dumps(update, indent=4)
    operations.handle_message.delay(update.get('message'),
                                    telegram_bot=bot)
    return ''


def main():
    app.run(host='0.0.0.0', port=config.PORT)

if __name__ in ('__main__', __bot_name__, ):
    main()

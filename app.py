# coding: utf-8
import json

import flask
from flask import request
import telegram
import time

import config
import operations

__bot_name__ = 'eth0_bot'
__author__ = 'Joker_Qyou'

app = None
bot = telegram.Bot(token=config.TOKEN)
bot.setWebhook('%s/%s' % (config.SERVER,
                          config.TOKEN.split(':')[-1], ))


def main():
    if config.WEBHOOK:
        global app, bot
        app = flask.Flask(__name__)
        app.debug = config.DEBUG

        @app.route('%s/%s' % (config.PATH, config.TOKEN.split(':')[-1], ),
                   methods=('POST', ))
        def webhook():
            ''' WebHook API func '''
            if app.debug:
                print json.dumps(request.json, indent=4)
            update = telegram.Update.de_json(request.json)
            operations.handle_update.delay(update,
                                           telegram_bot=bot)
            return ''

        if config.USE_NGINX:
            app.run(host='0.0.0.0', port=config.PORT)
        else:
            raise NotImplementedError('Not implemented yet, sorry')
            if 'SSL_CERT' not in dir(config)\
                    or 'SSL_KEY' not in dir(config):
                raise RuntimeError('Missing SSL cert or key')
            if config.DEBUG:
                app.logger.warn(('You are running Flask without nginx '
                                 'and having debug mode enabled'))
            app.run(host='0.0.0.0', port=config.PORT)
    else:
        while 1:
            time.sleep(config.FETCH_INTERVAL)
            updates = bot.getUpdates()
            for update in updates:
                operations.handle_update(update)

if __name__ in ('__main__', __bot_name__, ):
    main()

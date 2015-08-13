# coding: utf-8
import json
import logging
import threading
# import time

import telegram
import certifi
import paho.mqtt.client as mqtt

from utils import extract_texts

__config__ = 'config.json'


def on_msg(client, config, mqtt_msg):
    try:
        msg = json.loads(mqtt_msg.payload)
        t_msg = telegram.Message.de_json(msg)
        client.logger.debug(t_msg.message_id)
        return_msg = {
            'reply_to': msg,
            'text': u'Pi: {}'.format(handle_client_command(t_msg))
        }
        client.publish(config.get('return_topic'),
                       json.dumps(return_msg),
                       qos=config.get('qos'))
    except Exception as e:
        client.logger.warn(e)
        return


def handle_client_command(t_msg):
    command, options, words = extract_texts(t_msg.text)
    if command != 'pi':
        return u'并不懂你在说什么'
    subcommand = options[-1] if len(options) > 0 else '/ping'
    if subcommand in ('/ping', '/pong', ):
        return 'pong' if subcommand == '/ping' else 'ping'
    elif subcommand == '/uptime':
        try:
            import uptime
        except ImportError:
            return u'没有安装 uptime 模块哦'
        else:
            return u'启动于 北京时间 {}'.format(
                uptime.boottime().strftime('%Y-%m-%d %H:%M:%S')
            )
    elif subcommand == '/free':
        try:
            import psutil
        except ImportError:
            return u'没有安装 psutil 模块哦'
        else:
            memory_usage = psutil.virtual_memory()
            swap_usage = psutil.swap_memory()
            return (u'内存使用率 {:.2f}%，共有 {:d} MB\n'
                    u'SWAP 使用率 {:.2f}%，共有 {:d} MB').format(
                memory_usage.percent, memory_usage.total / 1024 / 1024,
                swap_usage.percent, swap_usage.total / 1024 / 1024
            )


def on_disconnect(client, config, return_code):
    client.logger.info(u'disconnected, code: %d, will reconnect', return_code)
    port = config.get('port', (8883 if config.get('use_ssl', False) else 1883))
    client.connect(
        config.get('host'),
        port=port,
        keepalive=config.get('keepalive', 60)
    )


def on_connect(client, config, flags, return_code):
    client.logger.info(u'connected, code: %d', return_code)
    client.logger.debug(u'subscribing %s', config.get('topic'))
    client.subscribe(str(config.get('topic')), config.get('qos'))


def on_subscribe(client, userdata, mid, granted_qos):
    client.logger.info(u'Subscribed with %s', granted_qos)


def on_publish(client, userdata, mid):
    client.logger.info(u'Message %s sent', str(mid))


class PiClient(threading.Thread):
    '''
    A client which connects to Mosca server and receive commands from there,
    and return local queried result.
    '''

    def __init__(self, mqtt_config, handlers):
        super(PiClient, self).__init__()
        self.config = mqtt_config
        self.__client = mqtt.Client(
            client_id=mqtt_config.get('client_id'),
            protocol=mqtt.MQTTv31,
            clean_session=mqtt_config.get('clean_session', True)
        )
        self.__init_logger()
        if mqtt_config.get('use_ssl', False):
            self.__client.tls_set(certifi.where())

        self.__client.username_pw_set(
            mqtt_config.get('username'),
            mqtt_config.get('password')
        )
        self.__client.user_data_set(self.config)

        self.__client.on_message = handlers.get('on_message', None)
        self.__client.on_subscribe = handlers.get('on_subscribe', None)
        self.__client.on_publish = handlers.get('on_publish', None)
        self.__client.on_disconnect = handlers.get('on_disconnect', None)
        self.__client.on_connect = handlers.get('on_connect', None)

        self._stop = threading.Event()

    def __init_logger(self):
        logger = logging.getLogger(__name__)
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        logger.addHandler(sh)
        logger.setLevel(logging.DEBUG)
        setattr(self.__client, 'logger', logger)

    def stop(self):
        self._stop.set()

    @property
    def stopped(self):
        return self._stop.isSet()

    def __reconnect(self):
        port = self.config.get(
            'port',
            (8883 if self.config.get('use_ssl', False) else 1883)
        )
        self.__client.connect(
            self.config.get('host'),
            port=port,
            keepalive=self.config.get('keepalive', 60)
        )
        self.__client.loop_forever()

    def run(self):
        try:
            self.__reconnect()
        except Exception:
            self.stop()
            print 'Stopped: ', self.stopped

handlers = {
    'on_message': on_msg,
    'on_subscribe': on_subscribe,
    'on_publish': on_publish,
    'on_connect': on_connect,
    'on_disconnect': on_disconnect,
}


def main():
    with open(__config__) as crf:
        config = json.load(crf)['mqtt']
        crf.close()
    config.update({
        'use_ssl': True,
        'client_id': 'pi_side',
    })

    while 1:
        try:
            client = PiClient(config, handlers)
            client.start()
            client.join()
        except Exception:
            if 'client' in locals():
                del client

if __name__ == '__main__':
    main()

# coding: utf-8
import json
import logging
# import time

import certifi
import paho.mqtt.client as mqtt

__config__ = 'config.json'

logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)


with open(__config__) as crf:
    config = json.load(crf)['mqtt']
    crf.close()


def on_msg(client, userdata, mqtt_msg):
    try:
        msg = json.loads(mqtt_msg.payload)
        print msg
    except Exception as e:
        print e
        return


def on_disconnect(client, userdata, return_code):
    logger.info(u'disconnected, code: %d, will reconnect', return_code)
    port = config.get('port', (8883 if config.get('use_ssl', False) else 1883))
    client.connect(
        config.get('host'),
        port=port,
        keepalive=config.get('keepalive', 60)
    )


def on_connect(client, userdata, flags, return_code):
    logger.info(u'connected, code: %d', return_code)
    client.subscribe(str(config.get('topic')), config.get('qos'))


def on_subscribe(client, userdata, mid, granted_qos):
    logger.info(u'Subscribed with %s', granted_qos)


def on_publish(client, userdata, mid):
    logger.info(u'Message %s sent', str(mid))


class PiClient(object):
    '''
    A client which connects to Mosca server and receive commands from there,
    and return local queried result.
    '''

    def __init__(self, mqtt_config, handlers):
        self.__client = mqtt.Client(
            client_id=mqtt_config.get('client_id'),
            protocol=mqtt.MQTTv31,
            clean_session=mqtt_config.get('clean_session', True)
        )
        if mqtt_config.get('use_ssl', False):
            self.__client.tls_set(certifi.where())

        self.__client.username_pw_set(
            config.get('username'),
            config.get('password')
        )

        self.__client.on_message = handlers.get('on_message', None)
        self.__client.on_subscribe = handlers.get('on_subscribe', None)
        self.__client.on_publish = handlers.get('on_publish', None)
        self.__client.on_disconnect = handlers.get('on_disconnect', None)
        self.__client.on_connect = handlers.get('on_connect', None)

        port = mqtt_config.get(
            'port',
            (8883 if mqtt_config.get('use_ssl', False) else 1883)
        )
        self.__client.connect(
            mqtt_config.get('host'),
            port=port,
            keepalive=mqtt_config.get('keepalive', 60)
        )
        self.__client.loop_forever()

config['use_ssl'] = True
handlers = {
    'on_message': on_msg,
    'on_subscribe': on_subscribe,
    'on_publish': on_publish,
    'on_connect': on_connect,
    'on_disconnect': on_disconnect,
}

client = PiClient(config, handlers)

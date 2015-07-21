# coding: utf-8
import json
import logging
import time

import certifi
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def on_msg(client, userdata, mqtt_msg):
    try:
        msg = json.loads(mqtt_msg.payload)
    except Exception as e:
        print e
        return


def on_disconnect(client, userdata, return_code):
    logger.info(u'disconnected, code: %d, will reconnect', return_code)
    client.connect(
        config.get('host'),
        port=config.get('port', (8883 if config.get('use_ssl', False) else 1883)),
        keepalive=config.get('keepalive', 60)
    )

def on_connect(client, userdata, flags, return_code):
    logger.info(u'connected, code: %d', return_code)

class PiClient(object):
    ''' A client which connects to Mosca server and receive commands from there, and return local queried result. '''

    def __init__(self, mqtt_config, handlers):
        self.__client = mqtt.Client(
            client=mqtt_config.get('client_id'),
            protocol=mqtt.MQTTv31, 
            clean_session=mqtt_config.get('clean_session', True)
        )
        if mqtt_config.get('use_ssl', False):
            self.__client.tls_set(certifi.where())

        self.__client.on_message = handlers.get('on_message', None)
        self.__client.on_subscribe = handlers.get('on_subscribe', None)
        self.__client.on_publish = handlers.get('on_publish', None)
        self.__client.on_disconnect = handlers.get('on_disconnect', None)
        self.__client.on_connect = handlers.get('on_connect', None)

        self.__client.connect(
            mqtt_config.get('host'),
            port=mqtt_config.get('port', (8883 if mqtt_config.get('use_ssl', False) else 1883)),
            keepalive=mqtt_config.get('keepalive', 60)
        )

client = PiClient({}, {})

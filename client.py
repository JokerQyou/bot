# coding: utf-8
import os
import sys
import traceback
from fractions import Fraction
import json
import logging
import threading
import time
from datetime import datetime

import telegram
import certifi
import paho.mqtt.client as mqtt

from utils import extract_texts

__config__ = 'config.json'
config = {}


def on_msg(client, config, mqtt_msg):
    try:
        msg = json.loads(mqtt_msg.payload)
        t_msg = telegram.Message.de_json(msg)
        client.logger.debug(t_msg.message_id)
        return_msg = {
            'reply_to': msg,
        }
        return_msg.update(handle_client_command(t_msg))
        client.publish(config.get('return_topic'),
                       json.dumps(return_msg),
                       qos=config.get('qos'))
    except Exception as e:
        client.logger.error(e)
        e_type, e_value, tb = sys.exc_info()
        client.logger.error('{0} - Uncaught exception: {1}: {2}\n{3}'.format(
            datetime.strftime(datetime.now(), '%H:%M:%S'),
            str(e_type), str(e_value), ''.join(traceback.format_tb(tb))
        ))


def handle_client_command(t_msg):
    global config
    command, options, words = extract_texts(t_msg.text)
    if command != 'pi':
        return {
            'text': u'并不懂你在说什么'}
    if len(options) > 0:
        subcommand = options[0][1:]  # drop the leading slash
    else:
        if len(words) > 0:
            subcommand = words[0]
        else:
            subcommand = 'ping'
    if subcommand in ('ping', 'pong', ):
        return {
            'text': ('pong' if subcommand == 'ping' else 'ping')
        }
    elif subcommand == 'uptime':
        try:
            import uptime
        except ImportError:
            return {
                'text': u'没有安装 uptime 模块哦'
            }
        else:
            return {
                'text': u'启动于 北京时间 {}'.format(
                    uptime.boottime().strftime('%Y-%m-%d %H:%M:%S')
                )
            }
    elif subcommand == 'free':
        try:
            import psutil
        except ImportError:
            return {
                'text': u'没有安装 psutil 模块哦'
            }
        else:
            memory_usage = psutil.virtual_memory()
            swap_usage = psutil.swap_memory()
            return {
                'text': (u'内存使用率 {:.2f}%，共有 {:d} MB\n'
                         u'SWAP 使用率 {:.2f}%，共有 {:d} MB').format(
                             memory_usage.percent, memory_usage.total / 1024 / 1024,
                             swap_usage.percent, swap_usage.total / 1024 / 1024
                    )
            }
    elif subcommand == 'photo':
        if t_msg.from_user.name != config['owner']\
                and t_msg.from_user.name[1:] != config['owner']:
            return {
                'text': u'区区凡人，竟敢对我下这种命令'
            }
        return {
            'photo': upload_photo()
        }
    else:
        return {
            'text': u'当听不懂你在说什么时，我会假装看风景'
        }


def upload_photo():
    '''上传照片到七牛，并返回私有链接地址'''
    from qiniu import Auth
    from qiniu import put_file
    import picamera
    import tempfile
    global config
    progress_handler = lambda progress, total: progress

    # Take a photo
    annotate_text = time.strftime('%Y/%m/%d %H:%M:%S')
    resolution = (800, 450, )
    with picamera.PiCamera() as camera:
        camera.annotate_text_size = 64
        camera.framerate = Fraction(15, 1)
        camera.awb_mode = 'fluorescent'
        camera.iso = 600
        fd, photo_path = tempfile.mkstemp(suffix='.jpg', prefix='pi')
        print fd, photo_path
        os.close(fd)
        time.sleep(1)  # wait a second for iso and white balance
        # and my camera is up side down, so rotate 180 deg
        camera.rotation = 180
        annotate_text = annotate_text + ' offset +1s'
        camera.annotate_text = annotate_text
        camera.capture(photo_path, resize=resolution)

    # Upload to qiniu
    mime_type = 'image/jpeg'
    auth = Auth(str(config['qiniu']['api_key']),
                str(config['qiniu']['secret']))
    print auth
    filename = os.path.basename(photo_path)
    print 'filename: ', filename, type(filename)
    token = auth.upload_token(str(config['qiniu']['bucket']))
    print token
    ret, info = put_file(token, filename, photo_path, {}, mime_type,
                         progress_handler=progress_handler)
    print 'uploaded: ', ret, info
    os.remove(photo_path)

    # Return URL
    base_url = '{}/{}'.format(str(config['qiniu']['domain']), filename)
    return auth.private_download_url(base_url, expires=3600)


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

    def loop(self):
        while 1:
            try:
                self.__client.loop_write()
                self.__client.loop_read()
                self.__client.loop_misc()
            except Exception as e:
                print 'Thread stop due to exception: ', e
                self.stop()
            finally:
                if self.stopped:
                    break

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
        self.loop()

    def run(self):
        return self.__reconnect()

handlers = {
    'on_message': on_msg,
    'on_subscribe': on_subscribe,
    'on_publish': on_publish,
    'on_connect': on_connect,
    'on_disconnect': on_disconnect,
}


def main():
    with open(__config__) as crf:
        global config
        config = json.load(crf)
        crf.close()
    config['mqtt'].update({
        'use_ssl': True,
        'client_id': 'pi_side',
    })

    while 1:
        try:
            client = PiClient(config['mqtt'], handlers)
            client.start()
            client.join()
        except Exception:
            if 'client' in locals():
                del client

if __name__ == '__main__':
    main()

# coding: utf-8
from datetime import datetime
from utils import extract_texts


def ping(msg=None, debug=False):
    '''检测机器人在线情况'''
    time_str = datetime.strftime(datetime.now(), '%m/%d %H:%M:%S')
    command, options, words = extract_texts(msg.text)
    response = 'pong' if command == 'ping' else 'ping'
    return u'%s (%s UTC)' % (response, time_str, )

pong = ping

# coding: utf-8
from datetime import datetime
from utils import extract_texts


def ping(msg=None, debug=False):
    ''' Ping the robot '''
    time_str = datetime.strftime(datetime.now(), '%m/%d %H:%M:%S')
    command, options, words = extract_texts(msg.get('text'))
    response = 'pong' if command == 'ping' else 'ping'
    return u'%s (%s UTC)' % (response, time_str, )

pong = ping

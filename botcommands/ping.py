# coding: utf-8
from datetime import datetime


def ping(msg=None, debug=False):
    ''' Ping the robot '''
    time_str = datetime.strftime('%m/%d %H:%M:%S')
    return u'pong (%s)' % time_str

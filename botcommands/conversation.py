# coding: utf-8
import config


def lsconversation(msg=None, debug=False):
    '''列出参与的所有会话'''
    conversations = config.get_hash('conversations')
    return '机器人酱参与的会话：\n%s' % '\n'.join(conversations.values())

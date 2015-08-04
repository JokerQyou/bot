# coding: utf-8
import config


@config.require_admin
def lsconversation(msg=None, debug=False):
    '''列出参与的所有会话'''
    conversations = config.get('conversations')
    return '机器人酱参与的会话：\n%s' % '\n'.join(conversations.values())

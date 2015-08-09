# coding: utf-8
from config import pi_command


@pi_command
def take_photo(msg=None, debug=False):
    '''拍摄一张照片'''
    # The actual operation is done on the RaspberryPi side
    return


@pi_command
def ping_pi(msg=None, debug=False):
    '''检测树莓派在线状态'''
    return

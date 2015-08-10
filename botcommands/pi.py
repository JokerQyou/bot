# coding: utf-8
from config import pi_command


@pi_command
def takephoto(msg=None, debug=False):
    '''拍摄一张照片'''
    # The actual operation is done on the RaspberryPi side
    return


@pi_command
def pingpi(msg=None, debug=False):
    '''检测树莓派在线状态'''
    return

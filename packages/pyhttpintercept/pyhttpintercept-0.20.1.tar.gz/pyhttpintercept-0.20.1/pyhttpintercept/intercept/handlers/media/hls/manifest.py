# encoding: utf-8

u""" Handler for HLS manifest file (.m3u8) requests. """

from pyhttpintercept import BodyInterceptHandler


class InterceptHandler(BodyInterceptHandler):
    I_CAN_HANDLE_THESE = [u'.m3u8',
                          u'.m3u']

# coding = utf-8
# pylint: disable=invalid-name
"""Net represents caffe::Net in C++"""
from __future__ import absolute_import
import os

from collections import defaultdict
import ctypes
from .base import LIB
from .base import c_str, py_str, check_call
from .base import NetHandle



class Net(object):
    """Net in caffe
    """

    def __init__(self, model_type):
        """create an net object

        Parameters
        ----------
        model_type: string
            chars 
            
        """
        if model_type == "chars":
            self.handle = NetHandle()
            model_dir = os.path.split(os.path.realpath(__file__))[0] + "/model-chars/"
            check_call(LIB.openNet(c_str(model_dir),ctypes.byref(self.handle)))


    def __del__(self):
        """destruct object
        """
        if hasattr(self, 'handle'):
            check_call(LIB.closeNet(self.handle))


    def ocr(self, image_file, context = '', text_len = 0):
        """ocr

        Parameters
        ==========
        image_file: string
            image file
        """
        out_buffer = ctypes.create_string_buffer(256)
        image_file1 = c_str(image_file)
        context1 = c_str(context)
        text_len1 = ctypes.c_int(text_len)
        ret = LIB.ocrNow(self.handle, image_file1, context1, text_len1, out_buffer)
        check_call(ret)
        str = out_buffer.value
        return py_str(str)

    @staticmethod
    def procImage(src_file, dest_file):
        """proc image
        Parameters
        ==========
        """
        check_call(LIB.procImage(c_str(src_file), c_str(dest_file)));

    @staticmethod
    def procImageDir(src_dir, dest_dir):
        """proc image dir
        Parameters
        ==========
        """
        check_call(LIB.procImageDir(c_str(src_dir), c_str(dest_dir)));

    @staticmethod
    def binaryImageDir(src_dir, dest_dir):
        """proc image dir
        Parameters
        ==========
        """
        check_call(LIB.binaryImageDir(c_str(src_dir), c_str(dest_dir)));

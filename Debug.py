#!/usr/bin/env python
import os, sys
import inspect
import re

DEBUG = True

class Debug(object):
    """
    Debug class, use to prettify debug print and mande them easily displayed or not by
    changig DEBUG value in this file
    """
    __color_list = ["\x1b[1;35m",
                    "\x1b[0;32m", "\x1b[0;33m", "\x1b[0;34m", "\x1b[0;35m"]
    __index, __len_color = 0, 6
    __mapping = dict()

    def __new__(cls, *args, **kwargs):
        """
        Overidde new to pick random color on instanciation
        :return: 
        """
        if DEBUG:
            frame = sys._getframe(1)
            caller = frame.f_code.co_name
            if (caller) in cls.__mapping.keys():
                instance = cls.__mapping[(caller)]
            else:
                cls.__index = (cls.__index + 1) % (cls.__len_color - 1)
                instance = object.__new__(cls)
            return instance

    def __init__(self, *args, **kwargs):
            self.color = self.__color_list[self.__index] + "["
            # get attribute
            frame = sys._getframe(1)
            self.function = frame.f_code.co_name
            self.base = inspect.getfile(frame).split("/")[-1][:-3]
            self.padding_length = len(self.function) + len(self.base) + 3
            self.padding = " " * self.padding_length
            print(self.padding)
            self.__mapping[self.function] = self
            self.display(*args, **kwargs)

    # def parse_and_format_args(self, *args, **kwargs):
    #     string = [self.color + self.base + "." + self.function + "]\x1b[0m"]
    #     rows, columns = os.popen('stty size', 'r').read().split()
    #     args_lengths = sum([len(str(a)) for a in args])
    #     max_lengths = max([len(a) + len(str(v)) for a, v in kwargs] + [args_lengths])
    #     print(max_lengths)
    #     if rows < len(sel@f.padding):
    #         string += ["\n"]
    #     print()

    def display(self, *args, **kwargs):
        # self.parse_and_format_args(*args, **kwargs)
        dbg_msg = " ".join(
             [str(arg) for arg in args] + ["\x1b[1;31m" + a + "\x1b[0m: " + str(kwargs[a]) for a in kwargs])
        print(self.color, self.base + '.' + self.function + "]\x1b[0m", dbg_msg)

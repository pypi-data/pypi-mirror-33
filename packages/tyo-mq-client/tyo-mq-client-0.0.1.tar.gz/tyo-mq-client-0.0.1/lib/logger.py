#
#
from __future__ import print_function
import sys

class Logger:
    instance = None

    def __init__(self, level):
        self.level = level

    @staticmethod
    def log(*args, **kwargs):
        print (args, kwargs)

    @staticmethod
    def error(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    @staticmethod
    def warn(*args, **kwargs):
        print (args, kwargs)

    @staticmethod
    def verbose(*args, **kwargs):
        print (args, kwargs)

    @staticmethod
    def debug(*args, **kwargs):
        print (args, kwargs)

    @staticmethod
    def info(*args, **kwargs):
        print (args, kwargs)
# -*- coding: utf-8 -*-
"""
zkb.log
~~~~~~~

A simple interface for logging and output.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

from __future__ import print_function
import sys
import time


class Logger(object):
    LOG_TRACE = 0
    LOG_DEBUG = 10
    LOG_INFO = 20
    LOG_WARN = 30
    LOG_ERROR = 40
    LOG_FATAL = 50

    def __init__(self, level=LOG_INFO, redirect=sys.stdout,
                 show_time=False, show_level=False):
        super(Logger, self).__init__()
        self.level = level
        self.redirect = redirect
        self.show_time = show_time
        self.show_level = show_level

    def _log(self, content, level=LOG_INFO):
        if level >= self.level:
            if self.show_level:
                content = '%s: %s' % (_get_level_string(level), content)
            if self.show_time:
                content = '[%s] %s' % (time.ctime(), content)
            print(content, file=self.redirect)

    def trace(self, content):
        self._log(content, Logger.LOG_TRACE)

    def debug(self, content):
        self._log(content, Logger.LOG_DEBUG)

    def info(self, content):
        self._log(content, Logger.LOG_INFO)

    def warn(self, content):
        self._log(content, Logger.LOG_WARN)

    def error(self, content):
        self._log(content, Logger.LOG_ERROR)

    def fatal(self, content):
        self._log(content, Logger.LOG_FATAL)


def _get_level_string(level):
    """Content log level to string that representing it.

    :param level: log level.
    :type level: int
    :rtype: str
    """
    if level >= Logger.LOG_FATAL:
        return 'FATAL'
    elif level >= Logger.LOG_ERROR:
        return 'ERROR'
    elif level >= Logger.LOG_WARN:
        return 'WARN'
    elif level >= Logger.LOG_INFO:
        return 'INFO'
    elif level >= Logger.LOG_DEBUG:
        return 'DEBUG'
    else:
        return 'TRACE'


#: Global logger
logger = Logger()

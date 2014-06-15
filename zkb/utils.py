# -*- coding: utf-8 -*-
"""
zkb.util
~~~~~~~~

This module contains utilities that will used in the project, including
constants, exceptions and so on.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

#: Default encoding used when reading or writing.
DEFAULT_ENCODING = 'utf-8'


class UnknownEncodingError(Exception):
    """An unknown encoding is being used to read or write.

    :param encoding: the encoding causing this error.
    :type encoding: str
    """

    def __init__(self, encoding):
        super(UnknownEncodingError, self).__init__()
        self.encoding = encoding

    def __str__(self):
        return repr(self.encoding)


class RequiredSettingIncorrectError(Exception):
    """A required setting cannot be found while reading settings.

    :param setting: the name of setting causing this error.
    :type setting: str
    """

    def __init__(self, setting):
        super(RequiredSettingIncorrectError, self).__init__()
        self.setting = setting

    def __str__(self):
        return repr(self.setting)


class UnknownBuilderError(Exception):
    """Unknown site builder is specified to build the site.

    :param name: the name of specified site builder.
    :type name: str
    """

    def __init__(self, name):
        super(UnknownBuilderError, self).__init__()
        self.name = name

    def __str__(self):
        return repr(self.name)

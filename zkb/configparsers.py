# -*- coding: utf-8 -*-
"""
zkb.configparsers
~~~~~~~~~~~~~~~~~

Parsers of header in headered file.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import yaml


class ConfigParser(object):
    """Base class of all config parsers.
    """

    def __init__(self):
        super(ConfigParser, self).__init__()

    def parse(self, config):
        """Parse a header config to dictionary.

        :param config: a string representing the config.
        :type config: str
        :return: result of parsing. None if parsing failed.
        :rtype: dict or None
        """
        pass


class YamlConfigParser(ConfigParser):
    """Parser for YAML config.
    """

    def __init__(self):
        super(YamlConfigParser, self).__init__()

    def parse(self, config):
        """Override to parse an YAML-formatted header config to dictionary.

        :param config: a string representing the YAML-formatted header.
        :type config: str
        :return: result of parsing. None if parsing failed.
        :rtype: dict or None
        """
        return yaml.load(config)

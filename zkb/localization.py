# -*- coding: utf-8 -*-
"""
zkb.localization
~~~~~~~~~~~~~~~~

Localization information for ZKB.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import yaml
import pkg_resources


_CACHE = {}


class LocalizationData(object):
    @classmethod
    def from_locale(cls, locale):
        if locale not in _CACHE:
            _CACHE[locale] = LocalizationData(locale)
        return _CACHE[locale]

    def __init__(self, locale):
        super(LocalizationData, self).__init__()
        self._load_data(locale)

    def _load_data(self, locale):
        parts = locale.split('_')
        if len(parts) != 1:
            parts = ['_'.join(parts[:-1]), parts[-1]]
        self._data = {}
        for index, _ in enumerate(parts):
            name = 'localization/%s.yml' % '_'.join(parts[:index + 1])
            try:
                with pkg_resources.resource_stream('zkb', name) as stream:
                    self._data.update(yaml.load(stream))
            except IOError:
                pass

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]
        else:
            return None

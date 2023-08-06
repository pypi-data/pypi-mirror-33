# -*- coding:utf-8 -*-

import six
import os
import json

from krux.types import Singleton
from krust.pather import *


class KonfCategory(object):
    def __init__(self, name, klass=None, init_arg=None, generator=None, konfer=None):
        self.name = name
        self.klass = klass
        self.init_arg = init_arg
        self.generator = generator
        self.konfer = konfer

    def get(self, key, *args):
        if isinstance(key, six.string_types):
            para = self.load_item(key)
        elif isinstance(key, dict):
            if self.klass is None:
                return key
            para = key
        else:
            raise KeyError(u'Not a valid key for KonfCategory {}: {}'.format(self.name, repr(key)))

        if self.init_arg is None:
            obj = self.klass(**para)
        else:
            obj = self.klass(**{self.init_arg: para})

        if self.generator is None:
            return obj
        else:
            return getattr(obj, self.generator)(*args)

    def load_item(self, key):
        item_name = os.path.join(self.name, key)
        item_path = self.konfer.pather[item_name]

        with open(item_path) as f:
            # TODO: jsmin
            return json.load(f, strict=False)


class Konfluence(Singleton):
    def __init__(self):
        if not os.getenv('KONFLUENCE_PATH'):
            self.pather = Pather(paths=['/etc/konfluence', '~/.konfluence', './konf'])
        else:
            self.pather = Pather(env_var='KONFLUENCE_PATH')

        self.categories = {}

    def register(self, name, klass=None, init_arg=None, generator=None):
        self.categories[name] = KonfCategory(name,
                                             klass=klass, init_arg=init_arg, generator=generator,
                                             konfer=self)

    def __getitem__(self, key):
        catname, sub = key.split('/', 1)
        return self._get_from_category(catname, sub)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            pass

        if default is None:
            return default
        elif isinstance(default, six.string_types):
            return self.__getitem__(default)
        else:
            catname, sub = key.split('/', 1)
            return self._get_from_category(catname, default)

    def _get_from_category(self, category, key):
        if not isinstance(category, KonfCategory):
            category = self.categories[category]

        if isinstance(key, six.string_types):
            tks = key.split(':')
            return category.get(*tks)
        elif isinstance(key, dict):
            return category.get(key)
        else:
            return key



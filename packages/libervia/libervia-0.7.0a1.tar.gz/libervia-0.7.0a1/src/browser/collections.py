#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2014 Jérôme Poisson <goffi@goffi.org>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class OrderedDict(object):
    """Naive implementation of OrderedDict which is compatible with pyjamas"""

    def __init__(self, *args, **kwargs):
        self.__internal_dict = {}
        self.__keys = [] # this list keep the keys in order
        if args:
            if len(args)>1:
                raise TypeError("OrderedDict expected at most 1 arguments, got {}".format(len(args)))
            if isinstance(args[0], (dict, OrderedDict)):
                for key, value in args[0].iteritems():
                    self[key] = value
            for key, value in args[0]:
                self[key] = value

    def __len__(self):
        return len(self.__keys)

    def __setitem__(self, key, value):
        if key not in self.__keys:
            self.__keys.append(key)
        self.__internal_dict[key] = value

    def __getitem__(self, key):
        return self.__internal_dict[key]

    def __delitem__(self, key):
        del self.__internal_dict[key]
        self.__keys.remove(key)

    def __contains__(self, key):
        return key in self.__keys

    def clear(self):
        self.__internal_dict.clear()
        del self.__keys[:]

    def copy(self):
        return OrderedDict(self)

    @classmethod
    def fromkeys(cls, seq, value=None):
        ret = OrderedDict()
        for key in seq:
            ret[key] = value
        return ret

    def get(self, key, default=None):
        try:
            return self.__internal_dict[key]
        except KeyError:
            return default

    def has_key(self, key):
        return key in self.__keys

    def keys(self):
        return self.__keys[:]

    def iterkeys(self):
        for key in self.__keys:
            yield key

    def items(self):
        ret = []
        for key in self.__keys:
            ret.append((key, self.__internal_dict[key]))
        return ret

    def iteritems(self):
        for key in self.__keys:
            yield (key, self.__internal_dict[key])

    def values(self):
        ret = []
        for key in self.__keys:
            ret.append(self.__internal_dict[key])
        return ret

    def itervalues(self):
        for key in self.__keys:
            yield (self.__internal_dict[key])

    def popitem(self, last=True):
        try:
            key = self.__keys.pop(-1 if last else 0)
        except IndexError:
            raise KeyError('dictionnary is empty')
        value = self.__internal_dict.pop(key)
        return((key, value))

    def setdefault(self, key, default=None):
        try:
            return self.__internal_dict[key]
        except KeyError:
            self[key] = default
            return default

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('udpate expected at most 1 argument, got {}'.format(len(args)))
        if args:
            if hasattr(args[0], 'keys'):
                for k in args[0]:
                    self[k] = args[0][k]
            else:
                for (k, v) in args[0]:
                    self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def pop(self, *args):
        if not args:
            raise TypeError('pop expected at least 1 argument, got 0')
        try:
            self.__internal_dict.pop(args[0])
        except KeyError:
            if len(args) == 2:
                return args[1]
            raise KeyError(args[0])
        self.__keys.remove(args[0])

    def viewitems(self):
        raise NotImplementedError

    def viewkeys(self):
        raise NotImplementedError

    def viewvalues(self):
        raise NotImplementedError

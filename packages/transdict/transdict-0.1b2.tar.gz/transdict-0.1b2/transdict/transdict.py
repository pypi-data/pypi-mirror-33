# Copyright (C) 2018 Ben Golightly <golightly.ben@googlemail.com>

# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# (https://www.gnu.org/licenses/license-list.en.html#GNUAllPermissive)



import collections.abc

identityfn = lambda x: x


class Transdict(collections.abc.Mapping):
    def __init__(self, source = {}):
        self._data = source

    def toKey(self, x):
        # Raise KeyError if invalid
        return x

    def fromKey(self, x):
        # Raise KeyError if invalid
        return x

    def fromValue(self, x):
        # Raise ValueError if invalid
        return x

    def __getitem__(self, key):
        key = self.toKey(key)
        value = self._data[key]
        return self.fromValue(value)

    def __iter__(self):
        for key in self._data.keys():
            try:
                yield self.fromKey(key)
            except KeyError:
                continue

    def __items__(self):
        for key, value in self._data.items():
            try:
                yield (self.fromKey(key), self.fromVaue(value))
            except KeyError:
                continue
            except ValueError:
                continue

    def __keys__(self):
        for key in self._data.keys():
            try:
                yield self.fromKey(key)
            except KeyError:
                continue

    def __values__(self):
        for value in self._data.values():
            try:
                yield self.fromValue(value)
            except ValueError:
                continue

    def __len__(self):
        return len(self._data)



class MutableTransdict(Transdict):
    def toValue(self, x):
        # Raise ValueError if invalid
        return x

    def __setitem__(self, key, value):
        key = self.toKey(key)
        value = self.toValue(value)
        self._data[key] = value



from os import path
import pickle

import numpy as np


class Buffer(object):

    def __init__(self, file=None):
        self._inner_buffer = []
        self._index = []
        self._updated = False
        self.file = file

    @property
    def buffered_index(self):
        return np.array(self._index)

    def __len__(self):
        return len(self._index)

    def __getitem__(self, item):
        ind = np.where(np.array(self._index) == item)[0]
        # if not found
        if ind.size == 0:
            return None
        else:
            ind = ind[0]
            return self._inner_buffer[ind]

    def __setitem__(self, key, value):
        if key in self._index:
            ind = np.where(np.array(self._index) == key)[0][0]
            self._inner_buffer[ind] = value
        else:
            self._index.append(key)
            self._inner_buffer.append(value)
        self._updated = True

    def set_if_empty(self, key, value):
        if self[key] is None:
            self[key] = value
        self._updated = True

    def update(self, key, value):
        self[key] = value

    def save(self, file=None):
        file = file or self.file
        if self._updated:
            with open(file, 'wb') as f:
                self._updated = False
                pickle.dump(self, f)

    @classmethod
    def from_pickle_file(cls, file):
        if path.exists(file):
            with open(file, 'rb') as f:
                buffer = pickle.load(f)
                buffer.file = file
            return buffer
        else:
            return Buffer(file)


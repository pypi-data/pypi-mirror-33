# encoding: utf-8

import os
import json
import codecs
from warnings import warn
from fdutil.path_tools import ensure_path_exists
from classutils.observer import ObservableMixIn


class JSONPersistentStore(object):
    def __init__(self,
                 root_folder):
        self.root_folder = root_folder
        ensure_path_exists(root_folder)

    def filename(self,
                 key):
        parts = key.split(u'/')[:-1]

        if len(parts) > 1:
            ensure_path_exists(os.path.join(self.root_folder, *parts[:-1]))

        if len(parts) == 0:
            return u'{p}.json'.format(p=self.root_folder)

        else:
            return u'{p}.json'.format(p=os.path.join(self.root_folder, *parts))

    @staticmethod
    def read_data(filepath):
        with codecs.open(filepath, 'r', 'utf-8') as data_file:
            return json.load(data_file)

    @staticmethod
    def write_data(filepath,
                   data):
        with codecs.open(filepath, 'w', "utf-8") as data_file:
            json.dump(data,
                      data_file,
                      indent=4)

    @staticmethod
    def _key(key):
        return key.split(u'/')[-1]

    def __setitem__(self,
                    key,
                    value):
        filename = self.filename(key)

        try:
            data = self.read_data(filename)

        except IOError:
            data = {}

        data[self._key(key)] = value
        self.write_data(filename, data)

    def __getitem__(self,
                    key):
        try:
            return self.read_data(self.filename(key))[self._key(key)]

        except IOError:
            raise KeyError(key)


class Persist(ObservableMixIn):

    """
    Add a key value pair to persistent storage
    e.g. to a database table given appropriate methods.

    The 'persistent store' needs to implement __getitem__ and __setitem__.
    """

    INITIAL_VALUE = u''

    def __init__(self,
                 persistent_store,
                 key,
                 init=None,
                 initial_value=None,
                 stack_level=2):

        """
        :param persistent_store: An object that gives access to the persistent
                                 store. It should implement __getitem__, raising
                                 KeyError if the item is not found. It should

        :param key: Name of thing we are storing, e.g. username
        :param init: Set this value in the persistent store if it's
                     not there already
        :param initial_value: Deprecated - use init instead
        """

        super(Persist, self).__init__()

        self.persistent_store = persistent_store
        self.key = key
        if initial_value is not None:
            warn(u'Persist.initial_value is deprecated, please use init instead.',
                 stacklevel=stack_level)
            if init is None:
                init = initial_value
            else:
                raise ValueError(u'Both init and initial_value supplied. Please use init')

        self.initial_value = (self.INITIAL_VALUE
                              if init is None
                              else init)

    @staticmethod
    def encode(value):
        """
        Overload this if you need to modify the value before storing
        e.g. Pickle
        """
        return value

    @staticmethod
    def decode(value):
        """
        Overload this if you need to modify the value after retrieving
        e.g. Unpickle
        """
        return value

    def __getitem__(self,
                    item):
        # Required to use nested Persist objects
        value = self.persistent_store[self.key]
        return value

    def set(self,
            value):
        self.persistent_store[self.key] = self.encode(value)
        self.notify_observers(key=self.key,
                              value=value)

    def get(self):
        try:
            return self.decode(self.persistent_store[self.key])
        except KeyError:
            self.set(self.initial_value)
            return self.initial_value

    @property
    def value(self):
        return self.get()

    @value.setter
    def value(self,
              value):
        self.set(value)


class PersistJSON(Persist):

    INITIAL_VALUE = {}

    @staticmethod
    def encode(value):
        return json.dumps(value)

    @staticmethod
    def decode(value):
        return json.loads(value)

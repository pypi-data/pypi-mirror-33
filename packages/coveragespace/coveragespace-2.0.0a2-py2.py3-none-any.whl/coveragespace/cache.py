import os
import pickle
import logging


log = logging.getLogger(__name__)


class Cache(object):

    PATH = os.path.join('.cache', 'coveragespace')

    def __init__(self):
        self._data = {}
        self._load()

    def _load(self):
        try:
            with open(self.PATH, 'rb') as fin:
                text = fin.read()
        except IOError:
            text = None

        try:
            data = pickle.loads(text)
        except (TypeError, KeyError, IndexError):
            data = None

        if isinstance(data, dict):
            self._data = data

    def _store(self):
        directory = os.path.dirname(self.PATH)
        if not os.path.exists(directory):
            os.makedirs(directory)

        text = pickle.dumps(self._data)
        with open(self.PATH, 'wb') as fout:
            fout.write(text)

    def set(self, key, value):
        try:
            url, data = key
        except ValueError:
            log.debug("Setting cache for %s", key)
        else:
            log.debug("Setting cache for %s: %s", url, data)
            key = self._slugify(*key)
        self._data[key] = value
        log.debug("Cached value: %s", value)
        self._store()

    def get(self, key, default=None):
        try:
            url, data = key
        except ValueError:
            log.debug("Getting cache for %s", key)
        else:
            log.debug("Getting cache for %s: %s", url, data)
            key = self._slugify(*key)
        value = self._data.get(key, default)
        log.debug("Cached value: %s", value)
        return value

    @staticmethod
    def _slugify(url, data):
        return (url, hash(frozenset(data.items())))

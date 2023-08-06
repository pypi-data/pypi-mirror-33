"""
Provides useful stuff, generally!
"""
from datetime import datetime
from collections import OrderedDict
from typing import Callable
from typing import Optional
import json

from pytz import timezone


class LimitedSizeDict(OrderedDict):
    """
    LimitedSizeDict pops items from the first if the size of dictionary exceeds
    the specified limit.
    """
    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop('size_limit', None)
        super(LimitedSizeDict, self).__init__(*args, **kwargs)
        self._check_size_limit()

    def __setitem__(self, *args, **kwargs):
        super(LimitedSizeDict, self).__setitem__(*args, **kwargs)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while self.size_limit < len(self):
                self.popitem(last=False)


class Cache:
    """
    A class to manage cache with IGitt and any other external application.

    The cache mechanism should be able to process raw JSON data. The response
    data from external requests is stored in the cache with the API URL of the
    associated IGitt object as the key and the data is stored along with its
    entity tag header, which is used alongside `If-None-Match` header for
    further queries using conditional requests. When an incoming webhook is
    received, the timestamp of reception is cached and any queries later on the
    same URL use the `If-Modified-Since` HTTP Header and the reception time
    using conditional requests, since the ETag Header is no longer valid. Note
    that conditional requests do not add up to rate limits on APIs.

    To use IGitt's caching mechanism for external request management, simply
    add the following code to your application before using IGitt.

    >>> from IGitt.Utils import Cache
    >>> Cache.use(read_from, write_to)

    If not provided, IGitt uses a default in-memory cache. For further details
    follow the specific method documentation below.
    """
    __mem_store = LimitedSizeDict(size_limit=10 ** 6)  # a million entries
    _get = __mem_store.__getitem__
    _set = __mem_store.__setitem__

    @classmethod
    def use(cls, read_from: Callable, write_to: Callable):
        """
        Connects the cache read, write functions to Cache class.

        :param read_from:
            The method to be called to fetch data from cache. It should be able
            to receive only one parameter, key, which is used to identify an
            entry uniquely in the cache.
        :param write_to:
            The method to be called to write data to cache. It should be able
            to receive two parameters, key (used to identify the entry in
            cache) and the item to be stored in cache, in the specified
            respective order.
        """
        cls._get = read_from
        cls._set = write_to

    @classmethod
    def validate(cls, item: dict) -> dict:
        """
        Checks if the given item has valid data and adds missing fields with
        default values. Expected fields are as follows.

        :type fromWebhook:  bool
        :type data:         object
        :type links:        dict
        :type lastUpdated:  str (formatted as '%a, %d %m %Y %H:%M:%S %Z')
        :type entityTag:    str or None

        :return:    The item dictionary after validation without any missing
                    fields. Also removes any additional unrelated fields from
                    the given dictionary.
        :raises:    TypeError, if the field does not match the expected type.
                    ValueError, if the type is correct, but the value is
                    invalid.
        """
        if 'data' not in item:
            item['data'] = {}

        if 'links' not in item:
            item['links'] = {}
        elif not isinstance(item['links'], dict):
            raise TypeError("'links' field should be a dictionary, not {}"
                            ''.format(type(item['links'])))

        if 'lastFetched' not in item:
            item['lastFetched'] = datetime.now(
                timezone('GMT')).strftime('%a, %d %m %Y %H:%M:%S %Z')
        else:
            # check if the datetime format is correct and raises an exception
            # if it is invalid. TypeError, if item['lastFetched'] is not a
            # string and ValueError, if the format doesn't match the expected.
            datetime.strptime(item['lastFetched'],
                              '%a, %d %m %Y %H:%M:%S %Z')

        if 'entityTag' not in item:
            item['entityTag'] = None
        elif (not isinstance(item['entityTag'], str) and
              item['entityTag'] != None):
            raise TypeError(
                "'entityTag' field should either be a string or None, not {}"
                ''.format(type(item['entityTag'])))

        if 'fromWebhook' not in item:
            item['fromWebhook'] = False
        elif not isinstance(item['fromWebhook'], bool):
            raise TypeError("'fromWebhook' field should be a bool, not {}"
                            ''.format(type(item['fromWebhook'])))

        # drop any other extra fields in the dictionary
        fields = {'fromWebhook', 'entityTag', 'lastFetched', 'links', 'data'}
        item = {k: v for k, v in item.items() if k in fields}

        return item

    @classmethod
    def get(cls, key) -> Optional[dict]:
        """
        Retrieves the entry from cache if present, otherwise None.
        """
        try:
            return cls.validate(json.loads(cls._get(key)))
        except (KeyError, TypeError):
            return None

    @classmethod
    def set(cls, key, item):
        """
        Stores the entry in cache.
        """
        item = cls.validate(item)
        cls._set(key, json.dumps(item))

    @classmethod
    def update(cls, key, new_value):
        """
        Updates the existing entry with new data, if present, otherwise creates
        a new entry in cache.
        """
        cls.set(key, {**(cls.get(key) or {}), **new_value})


class PossiblyIncompleteDict:
    """
    A dict kind of thing (only supporting item getting) that, if an item isn't
    available, gets fresh data from a refresh function.
    """

    def __init__(self, data: dict, refresh) -> None:
        self.may_need_refresh = True
        self._data = self._del_nul(data)
        self._refresh = refresh

    @staticmethod
    def _del_nul(elem):
        """
        elegantly tries to remove invalid \x00 chars from
        strings, strings in lists, strings in dicts.
        """
        if isinstance(elem, str):
            return elem.replace(chr(0), '')

        elif isinstance(elem, dict):
            return {key: PossiblyIncompleteDict._del_nul(value)
                    for key, value in elem.items()}

        elif isinstance(elem, list):
            return [PossiblyIncompleteDict._del_nul(item)
                    for item in elem]

        return elem

    def __getitem__(self, item):
        if item in self._data:
            return self._data[item]

        self.maybe_refresh()
        return self._data[item]

    def __setitem__(self, key, item):
        self._data[key] = item

    def __contains__(self, item):
        """
        Needed for determining if an item is in the possibly incomplete self.
        """
        return item in self._data

    def update(self, value: dict):
        """
        Updates the dict with provided dict.
        """
        self._data.update(self._del_nul(value))

    def maybe_refresh(self):
        """
        Refresh if it may need a refresh.
        """
        if self.may_need_refresh:
            self.refresh()

    def refresh(self):
        """
        Refreshes data unconditionally.
        """
        self._data = self._del_nul(self._refresh())
        self.may_need_refresh = False

    def get(self):
        """
        Returns the stored data.
        """
        return self._data


class CachedDataMixin:
    """
    You provide:

    - self._get_data for getting your data

    You can also create an IGitt instance with your own data using from_data
    classmethod.
    """
    default_data = {}  # type: dict

    @classmethod  # Ignore PyLintBear
    def from_data(cls, data: Optional[dict]=None, *args, **kwargs):
        """
        Returns an instance created from the provided data. No further requests
        are made.

        :raises TypeError:
            When the args provided are insufficient to call __init__.
        """
        instance = cls(*args, **kwargs)
        instance.data = data or {}

        return instance

    def _get_data(self):
        """
        Retrieves the data for the object.
        """
        raise NotImplementedError

    def refresh(self):  # dont cover
        """
        Refreshes all the data from the hoster!
        """
        if not getattr(self, '_data', None):
            self._data = PossiblyIncompleteDict(
                self.default_data, self._get_data)

        self._data.refresh()

    @property
    def data(self):
        """
        Retrieves the data, if needed from the network.
        """
        if not getattr(self, '_data', None):
            self._data = PossiblyIncompleteDict(
                self.default_data, self._get_data)

        return self._data

    @data.setter
    def data(self, value):
        """
        Setter for the data, use it to override, refresh, ...
        """
        self._data = PossiblyIncompleteDict(value, self._get_data)


def eliminate_none(data):
    """
    Remove None values from dict
    """
    return dict((k, v) for k, v in data.items() if v is not None)

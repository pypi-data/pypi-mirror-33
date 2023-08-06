# -*- coding: utf-8 -*-

import os
import time
import unittest
from cachingutil.file_cache import FileCache
from cachingutil.unittests.interval_tester import interval_cache_tester


class IntervalFileCache(FileCache):
    """
    simple cache for times. the time for each key
    will stay the same for the interval given by
    max_age on instantiation
    """

    def filename(self,
                 key):
        return u'{filename}.cache'.format(filename=key)

    def key(self,
            key):
        return key

    def fetch_from_source(self,
                          key):
        return int(time.time())

    @staticmethod
    def encode(data):
        return str(data)

    @staticmethod
    def decode(encoded):
        return int(encoded)


class TestFileCaching(unittest.TestCase):

    FOLDER = u'.{s}test_data{s}test_caching'.format(s=os.sep)
    MAX_AGE = 3

    def setUp(self):
        # Set up an Interval cache with values
        # expiring after 5s
        self.cache = IntervalFileCache(max_age=self.MAX_AGE,
                                       folder=self.FOLDER)

    def tearDown(self):
        for filename in (u'a',  u'b'):
            try:
                os.remove(self.cache.key(key=filename))
            except Exception:
                pass
        try:
            os.rmdir(self.FOLDER)
        except Exception:
            pass

    def test_key(self):

        data = {u'abc': u'abc.cache',
                u'temp/abc': u'temp/abc.cache'}
        for filename, path in iter(data.items()):
            self.assertEqual(self.cache.filepath(key=filename),
                             os.path.normpath(os.path.join(self.FOLDER, path)))

    test_fetch = interval_cache_tester

# -*- coding: utf-8 -*-

import time
import unittest
from cachingutil.memory_cache import SimpleMemoryCache
from cachingutil.unittests.interval_tester import interval_cache_tester


class IntervalMemoryCache(SimpleMemoryCache):
    """
    simple cache for times. the time for each key
    will stay the same for the interval given by
    max_age on instantiation
    """
    def key(self,
            key):
        return key

    def fetch_from_source(self,
                          key):
        return time.time()


class TestMemoryCaching(unittest.TestCase):

    def setUp(self):
        # Set up an Iterval cache with values
        # expiring after 3s
        self.cache = IntervalMemoryCache(max_age=3)

    def tearDown(self):
        pass

    test_fetch = interval_cache_tester
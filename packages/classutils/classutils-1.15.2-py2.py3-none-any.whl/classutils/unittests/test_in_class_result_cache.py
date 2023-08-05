# -*- coding: utf-8 -*-

import time
import unittest
from random import randint
from classutils import class_cache_result, clear_class_cached_results


class CachedProperties(object):

    def __init__(self):
        self.count = 0

    @property
    @class_cache_result
    def property_1(self):
        self.count += 1
        return self.count

    @property
    @class_cache_result
    def property_2(self):
        self.count += 1
        return self.count

    @property
    @class_cache_result(timeout=3)
    def property_3(self):
        self.count += 1
        return self.count

    @class_cache_result
    def args_1(self):
        self.count += 1
        return self.count

    @class_cache_result
    def args_2(self,
               p1,
               p2,
               p3=3,
               p4=4):
        return (p1 + p2 + p3 + p4) * randint(1, 1000)

    @clear_class_cached_results
    def reset(self):
        self.count = 0


class TestResettableCachedProperties(unittest.TestCase):

    def setUp(self):
        self.result_cacher = CachedProperties()

    def test_cached(self):
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)

        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)

    def test_cached_refresh(self):
        self.assertEqual(1, self.result_cacher.args_1())
        self.assertEqual(1, self.result_cacher.args_1())
        self.assertEqual(2, self.result_cacher.args_1(refresh=True))
        self.assertEqual(2, self.result_cacher.args_1())

    def test_cached_args(self):
        r_1_2 = self.result_cacher.args_2(1, 2)
        self.assertEqual(r_1_2, self.result_cacher.args_2(1, 2))
        self.assertEqual(r_1_2, self.result_cacher.args_2(1, 2))

        r_9_2 = self.result_cacher.args_2(9, 2)
        self.assertEqual(r_9_2, self.result_cacher.args_2(9, 2))
        self.assertEqual(r_9_2, self.result_cacher.args_2(9, 2))

        r_5_6_7_8 = self.result_cacher.args_2(5, 6, p3=7, p4=8)
        self.assertEqual(r_5_6_7_8, self.result_cacher.args_2(5, 6, p3=7, p4=8))
        self.assertEqual(r_5_6_7_8, self.result_cacher.args_2(5, 6, p3=7, p4=8))

        r_4_3_2_1 = self.result_cacher.args_2(4, 3, p3=2, p4=1)
        self.assertEqual(r_4_3_2_1, self.result_cacher.args_2(4, 3, p3=2, p4=1))
        self.assertEqual(r_4_3_2_1, self.result_cacher.args_2(4, 3, p3=2, p4=1))

        self.assertEqual(r_1_2, self.result_cacher.args_2(1, 2))
        self.assertEqual(r_9_2, self.result_cacher.args_2(9, 2))
        self.assertEqual(r_5_6_7_8, self.result_cacher.args_2(5, 6, p3=7, p4=8))
        self.assertEqual(r_4_3_2_1, self.result_cacher.args_2(4, 3, p3=2, p4=1))

    def test_cached_timeout(self):
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(3, self.result_cacher.property_3)

        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)

        time.sleep(1)

        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(3, self.result_cacher.property_3)
        self.assertEqual(3, self.result_cacher.property_3)

        time.sleep(2)

        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(4, self.result_cacher.property_3)
        self.assertEqual(4, self.result_cacher.property_3)

    def test_resetable(self):

        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(1, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_2)

        self.result_cacher.reset()

        self.assertEqual(1, self.result_cacher.property_2)
        self.assertEqual(1, self.result_cacher.property_2)
        self.assertEqual(2, self.result_cacher.property_1)
        self.assertEqual(2, self.result_cacher.property_1)


if __name__ == u'__main__':
    unittest.main()

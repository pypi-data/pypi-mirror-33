# -*- coding: utf-8 -*-
from test.base import PoolTestCase


class SimpleTestCase(PoolTestCase):

    def test_default_settings(self):
        self.assertIsNone(self.pool.default)
        self.assertIsNone(self.pool.module_lookup)
        self.assertFalse(self.pool.abstract)
        self.assertIs(self.pool.base_class, object)

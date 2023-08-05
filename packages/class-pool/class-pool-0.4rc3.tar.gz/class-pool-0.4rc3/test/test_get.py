# -*- coding: utf-8 -*-

"""Created on 21.06.18

.. moduleauthor:: Paweł Pecio
"""
from unittest.mock import Mock

from class_pool.pool import Pool
from test.base import PoolTestCase


class SimpleTestCase(PoolTestCase):

    def test_getter(self):

        class A(object):
            pass

        self.pool.register(A)
        self.assertIn('A', self.pool)
        self.assertIs(self.pool['A'], A)

    def test_get_method(self):

        class B(object):
            pass

        self.pool.register(B)
        self.assertIn('B', self.pool)
        self.assertIs(self.pool.get('B'), B)

    def test_get_default(self):

        class D(object):
            pass

        self.pool = Pool.new(base_class=object, default=D)

        self.assertIs(self.pool.get('notexist'), D)

    def test_get_default_callable(self):

        default = Mock()

        self.pool = Pool.new(base_class=object, default=default)
        self.pool.get('somethinddefault')

        default.assert_called_with('somethinddefault')

    def test_getter_exception(self):

        with self.assertRaises((KeyError,)):
            cls = self.pool['nocuchclass']

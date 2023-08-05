# -*- coding: utf-8 -*-

"""Created on 21.06.18

.. moduleauthor:: Paweł Pecio
"""

from class_pool.pool import Pool, PoolRegistrationError
from test.base import PoolTestCase


class RegisterationTestCase(PoolTestCase):

    def test_register_by_method(self):

        class A(object):
            pass

        self.pool.register(A)
        self.assertIn('A', self.pool)

    def test_register_override_id(self):

        class B(object):
            pass

        self.pool.register(B, forced_id='TestID')
        self.assertIn('TestID', self.pool)

    def test_register_exception(self):

        class Base(object):
            pass

        self.pool = Pool.new(base_class=Base)

        with self.assertRaises((PoolRegistrationError,)):
            self.pool.register(object)

    def test_register_silently(self):
        class Base(object):
            pass

        self.pool = Pool.new(base_class=Base)

        cid = self.pool.register(object, silently=True)
        self.assertIsNone(cid)

    def test_register_decorator_noargs(self):

        @self.pool.register
        class C(object):
            pass

        self.assertIn('C', self.pool)

    def test_register_decorator_emptyargs(self):

        @self.pool.register()
        class D(object):
            pass

        self.assertIn('D', self.pool)

    def test_register_metaclass(self):

        class E(metaclass=self.pool.metaclass()):
            pass

        self.assertIn('E', self.pool)

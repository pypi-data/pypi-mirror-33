# -*- coding: utf-8 -*-

"""Created on 22.06.18

.. moduleauthor:: Paweł Pecio
"""

from class_pool.pool import Pool
from test.base import PoolTestCase


class AutoLoadingTestCase(PoolTestCase):

    def test_loading(self):
        pool = Pool.new(base_class=object, module_lookup='foo')

        pool.populate(['test.snippet.auto', ])

        self.assertIn('Foo', pool)
        self.assertIn('Bar', pool)

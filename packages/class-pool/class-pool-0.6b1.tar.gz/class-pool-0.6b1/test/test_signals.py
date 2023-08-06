# -*- coding: utf-8 -*-

"""Created on 22.06.18

.. moduleauthor:: Paweł Pecio
"""
from unittest.mock import Mock

from test.base import PoolTestCase


class SignalsTestCase(PoolTestCase):

    def test_loading(self):

        handler = Mock()

        self.pool.on_register.add_handler(handler)

        class A(object):
            pass

        self.pool.register(A)
        handler.assert_called_with('A', A)

# -*- coding: utf-8 -*-

"""Created on 04.06.18

.. moduleauthor:: Paweł Pecio
"""
import warnings

_django_support = True

try:
    from django.db import models
except ImportError:
    warnings.warn("Trying to import django model field from. but django package"
                  "is not available.")

    _django_support = False

from .pool import PoolInterface


if _django_support:
    class PoolChoiceField(models.CharField):
        """
            Type choice field for django models which works with class pools.
        """

        exclude_types = ()

        def __init__(self, pool, *args, **kwargs):
            self._builded_choices = None

            assert isinstance(pool, PoolInterface), "Pool has to implement PoolInterface"
            self._pool = pool

            if 'choices' not in kwargs:
                kwargs['choices'] = self.build_choices()

            if 'max_length' not in kwargs:
                kwargs['max_length'] = 40

            super(PoolChoiceField, self).__init__(*args, **kwargs)

        def deconstruct(self):
            name, path, args, kwargs = super().deconstruct()
            # Only include kwarg if it's not the default
            kwargs.pop('choices', None)
            return name, path, args, kwargs

        @property
        def pool(self):
            return self._pool

        def build_choices(self):

            if self._builded_choices is None:

                self._builded_choices = list(
                    (type_code, getattr(klass, 'verbose_name', type_code))
                    for type_code, klass in self._pool if type_code not in self.exclude_types,
                )

            return self._builded_choices
else:
    def PoolChoiceField(*args, **kwargs):
        raise Exception("Django cannot be imported. Model field is not available")

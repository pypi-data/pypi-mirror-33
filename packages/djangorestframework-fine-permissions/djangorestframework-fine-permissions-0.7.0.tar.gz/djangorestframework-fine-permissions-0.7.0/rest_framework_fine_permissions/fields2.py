# -*- coding: utf-8 -*-

"""
"""

import logging
import six
import collections

from django.db import models
from rest_framework import serializers
from rest_framework.fields import Field, empty

from .utils import get_serializer

logger = logging.getLogger(__name__)


class ModelPermissionsField(Field):

    """ Field that acts as a ModelPermissionsSerializer for relations. """

    def __init__(self, serializer, **kwargs):
        self.serializer = get_serializer(serializer)
        self._cached_allowed_fields = {}#'kwargs.pop('cached_allowed_fields', {})
        # print('CAF : {}'.format(self._cached_allowed_fields))
        super(ModelPermissionsField, self).__init__(**kwargs)
        # print('BBBBB : {}'.format(self.__class__.__dict__))

    def to_representation(self, obj):
        """ Represent data for the field. """
        from .serializers import ModelPermissionsSerializer
        many = isinstance(obj, collections.Iterable) \
            or isinstance(obj, models.Manager) \
            and not isinstance(obj, dict)

        serializer_cls = get_serializer(self.serializer)

        assert serializer_cls is not None \
            and issubclass(serializer_cls, serializers.ModelSerializer), (
                "Bad serializer defined %s" % serializer_cls
            )

        extra_params = {}
        if issubclass(serializer_cls, ModelPermissionsSerializer):
            extra_params['cached_allowed_fields'] =\
                self.parent.cached_allowed_fields
                #self._cached_allowed_fields


        ser = self.serializer(obj, context=self.context, many=many,
                              **extra_params)

        # Append the serializer's authorized fields to its parent
        if hasattr(ser, 'cached_allowed_fields'):
            child_fields = ser.cached_allowed_fields
            # self.parent.cached_allowed_fields.update(child_fields)
        return ser.data

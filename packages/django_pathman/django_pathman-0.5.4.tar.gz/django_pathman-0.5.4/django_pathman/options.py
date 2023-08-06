# coding: utf-8

from django.db.models import options

partition_attr = 'partition'

options.DEFAULT_NAMES = options.DEFAULT_NAMES + (partition_attr, )


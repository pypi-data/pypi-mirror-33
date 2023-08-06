# coding: utf-8

from django.apps import AppConfig


class DjangoPathmanConfig(AppConfig):
    name = 'django_pathman'

    def ready(self):
        from autodetector import patch_autodetector
        patch_autodetector()
        super(DjangoPathmanConfig, self).ready()

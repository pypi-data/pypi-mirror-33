# -*- coding: utf-8 -*-

from django.apps import AppConfig


class NavsyConfig(AppConfig):

    name = 'navsy'
    verbose_name = 'Navigation'

    def ready(self):

        from navsy import cache, settings, signals

        settings.check_settings()
        cache.delete_data()


# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.db.utils import OperationalError


class NavsyConfig(AppConfig):

    name = 'navsy'
    verbose_name = 'Navigation'

    def ready(self):

        from navsy import cache, settings, signals
        from navsy.models import Page

        settings.check_settings()
        cache.clear()

        try:
            Page.update_tree()
        except OperationalError:
            pass

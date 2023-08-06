# -*- coding: utf-8 -*-

from django.utils.module_loading import import_string


def import_function(path):
    try:
        func = import_string(path)
        if hasattr(func, '__call__'):
            return func
        else:
            return None
    except ImportError:
        return None

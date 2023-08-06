# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils import translation

import re


def get_current_language():
    current_language = translation.get_language() or settings.LANGUAGE_CODE
    return current_language


def is_multilanguage():
    return bool(len(settings.LANGUAGES) > 1)


def split_languages(languages_codes_str):
    return re.findall(r'[\w\-]+', languages_codes_str.lower()
                      ) if languages_codes_str else []


def use_modeltranslation():
    if is_multilanguage():
        if 'modeltranslation' in settings.INSTALLED_APPS:
            try:
                import modeltranslation
                return True
            except ImportError:
                pass
    return False


# -*- coding: utf-8 -*-

from navsy.models import Page
from navsy.utils import i18n_utils


if i18n_utils.use_modeltranslation():

    try:
        from modeltranslation.translator import translator, TranslationOptions

        class PageTranslationOptions(TranslationOptions):
            fields = (
                'name', 'slug',
                'seo_title', 'seo_description', 'seo_keywords', )

        translator.register(Page, PageTranslationOptions)

    except ImportError:
        pass
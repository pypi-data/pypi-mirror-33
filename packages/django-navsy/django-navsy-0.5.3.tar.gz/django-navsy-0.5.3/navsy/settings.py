# -*- coding: utf-8 -*-

import django

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if django.VERSION < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

from navsy.exceptions import NoReverseMatch
from navsy.utils import i18n_utils


def check_settings():

    try:
        reverse('navsy-router')
    except NoReverseMatch:
        e = 'You must add "'
        e += 'url(r\'^\', include(\'navsy.urls\'))'
        e += '" to your urls.'
        raise ImproperlyConfigured(e)

    if i18n_utils.is_multilanguage():
        try:
            reverse('set_language')
        except NoReverseMatch:
            e = 'You must add "'
            e += 'url(r\'^i18n/\', include(\'django.conf.urls.i18n\'))'
            e += '" to your urls.'
            raise ImproperlyConfigured(e)

# -*- coding: utf-8 -*-

from django.conf import settings

from navsy.utils import i18n_utils


def data(request):
    d = {}
    d['navsy_debug'] = settings.DEBUG
    if request:
        d['navsy_host'] = '%s://%s' % (request.scheme, request.get_host(), )
        d.update(getattr(request, 'navsy_data', {}))
    d['navsy_multilanguage'] = i18n_utils.is_multilanguage()
    return d

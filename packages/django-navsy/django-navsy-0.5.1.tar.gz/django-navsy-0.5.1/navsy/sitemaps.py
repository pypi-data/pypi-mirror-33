# -*- coding: utf-8 -*-

from django.conf import settings
# https://docs.djangoproject.com/en/dev/ref/contrib/sitemaps/
from django.contrib.sitemaps import Sitemap
from django.utils import translation

from navsy.models import Page
from navsy.urls import reverse
from navsy.utils import i18n_utils


class ModelSitemap(Sitemap):

    """
    class MyModelSitemap(ModelSitemap):

        changefreq = 'weekly'
        priority = 0.5

        def items(self):
            return MyModel.objects.all()
    """

    def __init__(self, language=settings.LANGUAGE_CODE):
        self.language = language

    def location(self, item):
        url = None
        if i18n_utils.is_multilanguage():
            with translation.override(self.language):
                url = item.get_absolute_url()
        else:
            url = item.get_absolute_url()
        return url


class PageSitemap(Sitemap):

    def __init__(self, language=settings.LANGUAGE_CODE):
        self.language = language

    def items(self):
        pages_qs = Page.objects.filter(sitemap_item=True, status=Page.STATUS_PUBLISHED)
        pages_list = list(pages_qs)
        return pages_list

    def get_priority(self, item):
        return item.sitemap_priority or Page.SITEMAP_DEFAULT_PRIORITY

    def get_changefreq(self, item):
        return item.sitemap_changefreq or Page.SITEMAP_DEFAULT_CHANGEFREQ

    def location(self, item):
        url = None
        if i18n_utils.is_multilanguage():
            with translation.override(self.language):
                url = item.get_absolute_url()
        else:
            url = item.get_absolute_url()
        return url

    priority = get_priority
    changefreq = get_changefreq


class ViewSitemap(Sitemap):

    """
    data = {
        'home':{ # view_name
            'args':[],
            'kwargs':{},
            'priority':0.5, # 0.0 - 1.0
            'changefreq':'weekly' # daily, weekly, monthly, yearly
        },
    }
    """

    data = {}

    def __init__(self, data, language=settings.LANGUAGE_CODE):
        self.data = data
        self.language = language

    def items(self):
        return self.data.keys()

    def get_priority(self, view_name):
        return self.data[view_name].get('priority', 0.5)

    def get_changefreq(self, view_name):
        return self.data[view_name].get('changefreq', 'weekly')

    def location(self, view_name):
        view_data = self.data.get(view_name, {})
        kwargs = view_data.get('kwargs', {})
        args = view_data.get('args', [])
        url = None
        if i18n_utils.is_multilanguage():
            with translation.override(self.language):
                url = reverse(view_name, *args, **kwargs)
        else:
            url = reverse(view_name, *args, **kwargs)
        return url

    priority = get_priority
    changefreq = get_changefreq


def get_pages_sitemaps():
    sitemaps = {}
    if i18n_utils.is_multilanguage():
        for language in settings.LANGUAGES:
            language_code = language[0]
            sitemaps['pages_%s' % (language_code, )] = PageSitemap(language=language_code)
    else:
        sitemaps['pages'] = PageSitemap()
    return sitemaps


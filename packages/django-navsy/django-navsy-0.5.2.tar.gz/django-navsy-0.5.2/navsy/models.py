# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.encoding import python_2_unicode_compatible, force_text
try:
    from slugify import slugify
except ImportError:
    from django.utils.text import slugify

from treenode.cache import query_cache
from treenode.models import TreeNodeModel

from navsy.utils import import_function, path_utils, pattern_utils, url_utils


class Page(TreeNodeModel):

    treenode_display_field = 'name'

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)

    STATUS_DRAFT = 1
    STATUS_PUBLISHED = 2
    STATUS_UNPUBLISHED = 0
    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft', ),
        (STATUS_PUBLISHED, 'Published', ),
        (STATUS_UNPUBLISHED, 'Unpublished', ),
    )
    SITEMAP_PRIORITY_CHOICES = (
        ('0.0', '0.0', ),
        ('0.1', '0.1', ),
        ('0.2', '0.2', ),
        ('0.3', '0.3', ),
        ('0.4', '0.4', ),
        ('0.5', '0.5', ),
        ('0.6', '0.6', ),
        ('0.7', '0.7', ),
        ('0.8', '0.8', ),
        ('0.9', '0.9', ),
        ('1.0', '1.0', ),
    )
    SITEMAP_CHANGEFREQ_CHOICES = (
        ('always', 'always', ),
        ('hourly', 'hourly', ),
        ('daily', 'daily', ),
        ('weekly', 'weekly', ),
        ('monthly', 'monthly', ),
        ('yearly', 'yearly', ),
        ('never', 'never', ),
    )

    SITEMAP_DEFAULT_PRIORITY = '0.5'
    SITEMAP_DEFAULT_CHANGEFREQ = 'never'

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, blank=True, default='')

    is_home = models.BooleanField(default=False)
    in_menu = models.BooleanField(default=True)

    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=STATUS_DRAFT)

    seo_title = models.CharField(blank=True, max_length=100)
    seo_description = models.TextField(blank=True)
    seo_keywords = models.TextField(blank=True)

    sitemap_item = models.BooleanField(default=True)
    sitemap_priority = models.CharField(
        max_length=5,
        choices=SITEMAP_PRIORITY_CHOICES,
        default=SITEMAP_DEFAULT_PRIORITY,
        blank=True)
    sitemap_changefreq = models.CharField(
        max_length=50,
        choices=SITEMAP_CHANGEFREQ_CHOICES,
        default=SITEMAP_DEFAULT_CHANGEFREQ,
        blank=True)

    @staticmethod
    def create_default_page():
        if Page.objects.count() == 0:
            page_obj = Page.objects.create(name='Home', is_home=True, in_menu=False)
            page_obj.create_default_route()

    def create_default_route(self):
        return Route.objects.get_or_create(page=self, regex='')

    def update_unique_home(self):
        if self.is_home:
            Page.objects.exclude(pk=self.pk).update(is_home=False)

    def get_absolute_url(self):
        return url_utils.reverse_url(self.get_path())

    def get_path(self):
        if self.is_home:
            path = ''
        else:
            breadcrumbs = self.get_breadcrumbs()
            slugs = [page.slug for page in breadcrumbs if not page.is_home]
            path = path_utils.join_path_slugs(slugs)
        path = path_utils.fix_path(path)
        return path

    def get_route(self):
        from navsy import cache
        return cache.get_route_by_page(self)

    @property
    def is_draft(self):
        statuses = self.get_breadcrumbs('status')
        statuses_flags = [(status == Page.STATUS_DRAFT) for status in statuses]
        return any(statuses_flags) and not self.is_unpublished

    @property
    def is_published(self):
        statuses = self.get_breadcrumbs('status')
        statuses_flags = [(status == Page.STATUS_PUBLISHED) for status in statuses]
        return all(statuses_flags)

    @property
    def is_unpublished(self):
        statuses = self.get_breadcrumbs('status')
        statuses_flags = [(status == Page.STATUS_UNPUBLISHED) for status in statuses]
        return any(statuses_flags)

    @property
    def path(self):
        return self.get_path()

    @property
    def route(self):
        return self.get_route()

    @property
    def url(self):
        return self.get_absolute_url()

    def save(self, *args, **kwargs):

        page_obj = self
        page_obj.slug = slugify(page_obj.name)

        for lang_code, lang_display in settings.LANGUAGES:
            lang_code = lang_code.replace('-', '_').lower()

            name_field = 'name_%s' % (lang_code, )
            slug_field = 'slug_%s' % (lang_code, )

            if hasattr(page_obj, name_field) and hasattr(page_obj, slug_field):
                name_value = str(getattr(page_obj, name_field, ''))
                slug_value = slugify(name_value)
                setattr(page_obj, slug_field, slug_value)

        super(Page, page_obj).save(*args, **kwargs)

    class Meta(TreeNodeModel.Meta):
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'


@python_2_unicode_compatible
class Route(models.Model):

    page = models.ForeignKey(
        'navsy.Page', blank=True, null=True,
        on_delete=models.CASCADE, related_name='routes')

    REGEX_CHOICES = pattern_utils.get_regex_choices()
    regex = models.CharField(
        max_length=255, blank=True, default='', choices=REGEX_CHOICES)

    view_name = models.CharField(
        max_length=100, unique=True, blank=True, null=True, db_index=True,
        help_text='(unique name used for reverse URL)')
    view_function_path = models.CharField(
        max_length=100, blank=True, help_text='(ex. app.views.view_func)')
    view_template_path = models.CharField(
        max_length=100, blank=True, help_text='(ex. app/template.html)')

    redirect_to_page = models.ForeignKey(
        'navsy.Page', blank=True, null=True, on_delete=models.SET_NULL)
    redirect_to_path = models.CharField(max_length=200, blank=True)
    redirect_to_url = models.URLField(blank=True)

    is_enabled = models.BooleanField(default=True)

    priority = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(9999)])

    def get_absolute_base_url(self):
        page_obj = self.get_page()
        return page_obj.get_path() if page_obj else ''

    def get_absolute_url_format(self):
        return path_utils.fix_path(
            self.get_absolute_base_url(), self.get_regex_format())

    def get_absolute_url_regex(self):
        return pattern_utils.get_regex_re(
            self.get_absolute_base_url(), self.regex)

    def get_absolute_url(self, parameters=None):
        return url_utils.reverse_url(
            url_utils.format_url(
                self.get_absolute_url_format(), parameters))

    def get_page(self):
        return query_cache(Page, pk=self.page_id) if self.page_id else None

    def get_redirect_url(self):
        redirect_url = None
        if self.redirect_to_page:
            redirect_url = self.redirect_to_page.get_absolute_url()
        elif self.redirect_to_url:
            redirect_url = self.redirect_to_url
        elif self.redirect_to_path:
            if self.redirect_to_path.startswith('/'):
                redirect_path = self.redirect_to_path
            else:
                page_obj = self.get_page()
                redirect_path = page_obj.get_absolute_url() if page_obj else '/'  # base_url
            redirect_url = path_utils.fix_path(
                redirect_path, self.redirect_to_path)
        # if redirect_url:
        #    print(redirect_url)
        return redirect_url

    def get_regex_display(self):
        return pattern_utils.get_regex_display(self.regex)

    def get_regex_format(self):
        return pattern_utils.get_regex_format(self.regex)

    def get_response(self, request, *args, **kwargs):

        if not self.has_response(request):
            raise Http404

        redirect_url = self.get_redirect_url()
        if redirect_url:
            return HttpResponseRedirect(redirect_url)

        data = {
            'navsy_page': self.get_page(),
            'navsy_route': self,
            'navsy_route_args': args,
            'navsy_route_kwargs': kwargs,
        }

        request.navsy_data = data

        if self.view_template_path:
            return render(request, self.view_template_path)

        if self.view_function_path:
            view_function = import_function(self.view_function_path)
            if view_function:
                if kwargs:
                    view_response = view_function(request, **kwargs)
                elif args:
                    view_response = view_function(request, *args)
                else:
                    view_response = view_function(request)

                if isinstance(view_response, HttpResponse):
                    return view_response
                else:
                    raise Exception('View function "%s" doesn\'t return \
                        an HttpResponse object.' % (self.view_function_path, ))
            else:
                # this should never happen since there is form validation
                raise Exception('View function "%s" is not \
                    a valid function.' % (self.view_function_path, ))

        if settings.DEBUG:
            return render(request, 'navsy/default.html')
        else:
            return HttpResponse('')

    def has_response(self, request=None):
        if self.is_enabled:
            page_obj = self.get_page()
            if page_obj:
                if request:
                    user = getattr(request, 'user', None)
                    if user:
                        if user.is_staff or user.is_superuser:
                            return page_obj.is_published or page_obj.is_draft
                return page_obj.is_published
            return True
        else:
            return False

    @property
    def redirect_url(self):
        return self.get_redirect_url()

    @property
    def regex_display(self):
        return self.get_regex_display()

    @property
    def regex_format(self):
        return self.get_regex_format()

    @property
    def url(self):
        return self.get_absolute_url()

    def save(self, *args, **kwargs):
        if self.view_name:
            self.view_name = self.view_name.strip()
        if not self.view_name:
            self.view_name = None
        super(Route, self).save(*args, **kwargs)

    class Meta:
        unique_together = (('page', 'regex', ), )
        ordering = ['page', '-priority', 'regex']
        # ordering = ['-priority', 'regex', 'page']
        verbose_name = 'Route'
        verbose_name_plural = 'Routes'

    def __str__(self):
        return force_text(self.get_absolute_url_format())

# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from treenode.admin import TreeNodeModelAdmin

from navsy.forms import PageForm, RouteForm, RouteInlineForm
from navsy.models import Page, Route
from navsy.utils import import_function, i18n_utils, url_utils

__PageAdminBaseClass = TreeNodeModelAdmin

if i18n_utils.use_modeltranslation():

    from modeltranslation.admin import TabbedTranslationAdmin
    from modeltranslation.utils import get_translation_fields

    class __PageAdminBaseClass(TreeNodeModelAdmin, TabbedTranslationAdmin):
        pass


class RouteAdmin(admin.ModelAdmin):

    form = RouteForm

    list_display = ('url_display_with_redirect',
                    'view_name', 'view_function_path', 'view_check',
                    'response_type', 'is_enabled', 'priority', )
    list_editable = ('view_name', 'view_function_path', 'is_enabled', 'priority', )
    save_on_top = True

    def url_display_with_redirect(self, obj):

        obj_style = '' if obj.has_response() else 'opacity: 0.5;'
        obj_html = ''
        obj_html += '<span style="%s">' % obj_style
        obj_html += obj.get_absolute_url_format()

        redirect_url = obj.get_redirect_url()
        if redirect_url:
            redirect_label_style = 'color: #AAAAAA; font-weight: normal;'
            redirect_url_style = 'color: #888888; font-weight: normal;'
            redirect_html = '&searr; \
                <small style="%s">redirect: </small>\
                <small style="%s">%s</small>\
                ' % (redirect_label_style, redirect_url_style, redirect_url, )
            obj_html += '<br>%s' % (redirect_html, )

        obj_html += '</span>'
        return obj_html

    url_display_with_redirect.short_description = 'URL'
    url_display_with_redirect.allow_tags = True

    def response_type(self, obj):

        badge_style = u'background-color: #CCCCCC; \
                        color: #FFFFFF; \
                        text-transform: uppercase; \
                        padding: 2px 6px; \
                        border-radius: 4px; \
                        margin-right: 5px;'

        badge_format = u'<small style="%s">%s</small>'

        if obj.view_function_path:
            return badge_format % (badge_style, _('function'), )

        elif obj.view_template_path:
            return badge_format % (badge_style, _('template'), )

        elif obj.get_redirect_url():
            return badge_format % (badge_style, _('redirect'), )
        else:
            return None

    response_type.allow_tags = True
    response_type.short_description = 'Response Type'

    def view_check(self, obj):

        if obj.view_function_path:
            return import_function(obj.view_function_path) is not None

        elif obj.view_template_path:
            try:
                view_template = get_template(obj.view_template_path)
                return True
            except Exception:
                return False

        return None

    view_check.short_description = 'View Check'
    view_check.boolean = True

    def get_fieldsets(self, request, obj=None):

        fieldsets = (
            (None, {
                'classes': ('wide', ),
                'fields': (
                    'page', 'regex', 'is_enabled',
                )
            }),
            ('Redirect', {
                'classes': ('wide', ),
                'fields': (
                    'redirect_to_page', 'redirect_to_path', 'redirect_to_url',
                )
            }),
            ('View', {
                'classes': ('wide', ),
                'fields': (
                    'view_name', 'view_function_path', 'view_template_path',
                )
            }),
        )

        return fieldsets

    def get_changelist_form(self, request, **kwargs):
        return RouteForm

admin.site.register(Route, RouteAdmin)


class RouteInline(admin.TabularInline):

    model = Route
    form = RouteInlineForm
    fk_name = 'page'
    extra = 0
    fields = ('regex', 'view_function_path', 'view_name',
              'is_enabled', 'priority', 'route_admin_link', )
    readonly_fields = ('route_admin_link', )
    view_on_site = False
    show_change_link = True

    def route_admin_link(self, obj):
        link_style = 'padding:6px 12px; line-height:25px; '
        if obj.id:
            link_href = url_utils.get_admin_change_url(obj)
        else:
            link_href = '#'
            link_style += 'opacity:0.2; pointer-events:none;'
        return u'<a href="%s" target="_self" class="button" style="%s">%s</a>\
                ' % (link_href, link_style, _('Change'), )

    route_admin_link.allow_tags = True
    route_admin_link.short_description = 'Options'


class PageAdmin(__PageAdminBaseClass):

    treenode_accordion = True

    form = PageForm

    def get_changelist_form(self, request, **kwargs):
        return PageForm

    def status_check(self, obj):
        if obj.is_draft:
            return None
        elif obj.is_published:
            return True
        elif obj.is_unpublished:
            return False
        else:
            return False

    status_check.short_description = 'Status Check'
    status_check.boolean = True

    list_display = ('url_with_link', 'status', 'status_check', 'is_home', 'in_menu', 'tn_priority', )
    list_editable = ('is_home', 'in_menu', 'status', 'tn_priority', )
    list_per_page = 100
    save_on_top = True

    def url_with_link(self, obj):
        obj_route = obj.get_route()
        obj_style = '' if obj_route and obj_route.has_response() else 'opacity: 0.5;'
        obj_url = obj.get_absolute_url()
        return u'<a style="%s" href="%s">%s</a>' % (obj_style, obj_url, obj_url, )

    url_with_link.short_description = 'URL'
    url_with_link.allow_tags = True

    inlines = [RouteInline]

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':80})},
    }

    def get_fieldsets(self, request, obj=None):

        if i18n_utils.use_modeltranslation():
            none_fields = ('tn_parent', ) + tuple(get_translation_fields('name'))
            seo_fields = tuple(get_translation_fields('seo_title')) + \
                         tuple(get_translation_fields('seo_description')) + \
                         tuple(get_translation_fields('seo_keywords'))
        else:
            none_fields = ('tn_parent', 'name', 'status', )
            seo_fields = ('seo_title', 'seo_description', 'seo_keywords', )

        sitemap_fields = ('sitemap_item', 'sitemap_priority', 'sitemap_changefreq', )

        fieldsets = (
            (None, {
                'classes': ('wide', ),
                'fields': none_fields
            }),
            ('SEO'.upper(), {
                'classes': ('collapse', ),
                'fields': seo_fields
            }),
            ('Sitemap'.upper(), {
                'classes': ('collapse', ),
                'fields': sitemap_fields
            }),
        )

        return fieldsets

    def save_related(self, request, form, formsets, change):
        super(PageAdmin, self).save_related(request, form, formsets, change)
        page_obj = form.instance
        page_obj.create_default_route()

admin.site.register(Page, PageAdmin)

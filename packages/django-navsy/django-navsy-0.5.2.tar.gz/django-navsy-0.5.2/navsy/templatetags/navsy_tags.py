# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from navsy import cache
from navsy.exceptions import NoReverseMatch
from navsy.models import Page, Route
from navsy.urls import reverse
from navsy.utils import i18n_utils

import re

try:
    basestring
except NameError:
    basestring = str

register = template.Library()

try:
    assignment_tag = register.assignment_tag
except AttributeError:
    assignment_tag = register.simple_tag


def __get_context_data(context):

    data = {
        'request':
            context.get('request', None),
        'navsy_host':
            context.get('navsy_host', None),
        'navsy_multilanguage':
            context.get('navsy_multilanguage', False),
        'navsy_page':
            context.get('navsy_page', None),
        'navsy_route':
            context.get('navsy_route', None),
        'navsy_route_args':
            context.get('navsy_route_args', None),
        'navsy_route_kwargs':
            context.get('navsy_route_kwargs', None),
        'navsy_model':
            context.get('navsy_model', None),
    }
    # print(data)
    return data


@register.inclusion_tag('navsy/breadcrumbs.html', takes_context=True)
def navsy_breadcrumbs(context):

    data = __get_context_data(context)
    page = data.get('navsy_page')
    data['breadcrumbs'] = page.get_breadcrumbs() if page else []
    return data


@assignment_tag(takes_context=True)
def navsy_is(context, target, value=True):

    data = __get_context_data(context)
    route_obj = data.get('navsy_route')

    if route_obj:

        if isinstance(target, Page):
            target_route_obj = cache.get_route_by_page(target)
            if target_route_obj:
                view_names = [target_route_obj.view_name]

        elif isinstance(target, Route):
            target_route_obj = target
            view_names = [target_route_obj.view_name]

        elif isinstance(target, basestring):
            view_names = re.findall(r'[\w\-\_]+', target)

        else:
            # raise Exception('target can be: view_name(s) string, Route instance, Page instance')
            pass

        if len(view_names):
            route_view_name = route_obj.view_name
            for view_name in view_names:
                if view_name and route_view_name:
                    if view_name == route_view_name:
                        return value

    return False


@register.simple_tag(takes_context=True)
def navsy_language_label(context, language, label=None):

    label = label or context.get('label', None)
    value = ''

    if label == 'code':
        value = language.get('code', '')
        value = value.upper()

    elif label == 'name':
        value = language.get('name_local', '')
        value = value.title()

    elif label == 'short_name':
        value = language.get('name_local', '')
        if len(value) > 3:
            value = value[:3]
        value = value.upper()

    else:
        value = language.get('code', '')
        value = value.upper()

    return value


@register.inclusion_tag('navsy/languages-alternate-href.html', takes_context=True)
def navsy_languages_alternate_href(context, languages=None):

    data = __get_context_data(context)
    data.update({
        # 'multilanguage': settings.NAVSY_MULTILANGUAGE,
        'languages_filter': i18n_utils.split_languages(languages),
    })
    return data


@register.inclusion_tag('navsy/languages-menu.html', takes_context=True)
def navsy_languages_menu(context, languages=None, label=None, select=False):

    data = __get_context_data(context)
    data.update({
        # 'multilanguage': settings.NAVSY_MULTILANGUAGE,
        'languages_filter': i18n_utils.split_languages(languages),
        'languages_label': label,
        'languages_select': select,
    })
    return data


@register.inclusion_tag('navsy/menu.html', takes_context=True)
def navsy_menu(context, select=False, label=None, levels=None):

    data = __get_context_data(context)
    data['menu_root'] = True
    data['menu_tree'] = Page.get_tree()
    data['menu_select'] = select
    data['menu_label'] = label
    data['menu_level'] = 0
    data['menu_levels'] = levels
    try:
        data['menu_levels'] = int(data['menu_levels'])
    except TypeError:
        data['menu_levels'] = None
    return data


@register.simple_tag(takes_context=True)
def navsy_meta_description(context, html=False, field=None):

    data = __get_context_data(context)
    page = data.get('navsy_page')
    model = data.get('navsy_model')

    description = ''

    for obj in [model, page]:
        for attr in [field, 'seo_description', 'description']:
            if attr and hasattr(obj, attr):
                value = getattr(obj, attr)
                if value and isinstance(value, basestring):
                    description = value
                    break
        else:
            continue
        break

    description = strip_tags(description)
    description = description.strip()
    description = truncatechars(description, 160)

    if html:
        description_html = '<meta name="description" content="%s" />' % (description, )
        description_html = mark_safe(description_html)
        return description_html
    else:
        return description


@register.simple_tag(takes_context=True)
def navsy_meta_keywords(context, html=False, field=None):

    data = __get_context_data(context)
    page = data.get('navsy_page')
    model = data.get('navsy_model')

    keywords = ''

    for obj in [model, page]:
        for attr in [field, 'seo_keywords', 'keywords']:
            if attr and hasattr(obj, attr):
                value = getattr(obj, attr)
                if value and isinstance(value, basestring):
                    keywords = value
                    break
        else:
            continue
        break

    keywords = keywords.strip()

    if html:
        keywords_html = '<meta name="keywords" content="%s" />' % (keywords, )
        keywords_html = mark_safe(keywords_html)
        return keywords_html
    else:
        return keywords


@register.simple_tag(takes_context=True)
def navsy_page_label(context, page, label=None):

    label = label or context.get('label', None)
    value = ''

    if label == 'name':
        value = page.name

    elif label == 'flat':
        value = page.name

    elif label == 'path':
        value = ' / '.join(page.get_breadcrumbs('name'))

    elif label == 'dash':
        page_ancestors_count = page.get_ancestors_count()
        if page_ancestors_count:
            value = '- ' * page_ancestors_count
        value += page.name

    elif label == 'tabs':
        page_ancestors_count = page.get_ancestors_count()
        if page_ancestors_count:
            value = '&mdash; ' * page_ancestors_count
        value += page.name

    else:
        value = page.name

    value = mark_safe(value)
    return value


# @register.inclusion_tag('navsy/pagination.html', takes_context=True)
# def navsy_pagination(context, select=False):
#     pass


@register.simple_tag(takes_context=True)
def navsy_title(context, base=None, html=False, field=None):

    data = __get_context_data(context)
    page = data.get('navsy_page')
    model = data.get('navsy_model')

    titles = []
    title = ''

    if page and page.is_home:
        title = page.seo_title or base
        title = title.strip()
    else:
        if model:
            for attr in [field, 'seo_title', 'title', 'name']:
                if attr and hasattr(model, attr):
                    value = getattr(model, attr)
                    if value:
                        titles.append(value)
                        break

            if not len(titles):
                titles.append(str(model))

        if page:
            names = page.get_breadcrumbs('name')
            if page.seo_title:
                names[-1] = page.seo_title
            titles += list(reversed(names))

        title = ' - '.join(titles)

        if base:
            if title:
                title += ' | '
            title += base.strip()

    if html:
        title_html = '<title>%s</title>' % (title, )
        title_html = mark_safe(title_html)
        return title_html
    else:
        return title


@register.simple_tag(takes_context=True)
def navsy_url(context, view_name=None, *args, **kwargs):

    url = ''

    if view_name:
        try:
            if kwargs:
                url = reverse(view_name, **kwargs)
            elif args:
                url = reverse(view_name, *args)
            else:
                url = reverse(view_name)

        except KeyError:
            # kwargs contains an argument with an invalid type
            url = reverse(view_name)

        except TypeError:
            # args contains an argument with an invalid type
            url = reverse(view_name)

        except NoReverseMatch:
            pass
    else:
        data = __get_context_data(context)
        model = data.get('navsy_model', None)

        if model:
            url = model.get_absolute_url()
        else:
            route_obj = data.get('navsy_route', None)
            route_args = data.get('navsy_route_args', [])
            route_kwargs = data.get('navsy_route_kwargs', {})
            if route_obj:
                url = route_obj.get_absolute_url(parameters=route_kwargs)

        if not url:
            url = '/'

        # append query string
        request = data.get('request')
        if request.GET:
            request_get = request.GET.copy()
            for k in kwargs:
                request_get[k] = kwargs[k]
            url += '?' + request_get.urlencode()

    # print(url)
    return url

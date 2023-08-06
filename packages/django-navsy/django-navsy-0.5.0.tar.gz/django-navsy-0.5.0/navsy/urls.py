# -*- coding: utf-8 -*-

import django

if django.VERSION < (2, 0):
    from django.conf.urls import url as re_path
else:
    from django.urls import re_path

from navsy.cache import get_route_by_view_name
from navsy.exceptions import NoReverseMatch
# from navsy.models import Route
from navsy.views import router


def reverse(view_name, *args, **kvargs):

    if args and kvargs:
        raise Exception('reverse cannot receive both *args and **kvargs')
    elif args:
        parameters = list(args)
    elif kvargs:
        parameters = dict(kvargs)
    else:
        parameters = None

    # print('reverse parameters: %s' % (parameters, ))

    # try:
    #     route_obj = Route.objects.get(view_name=view_name)
    #     return route_obj.get_absolute_url(parameters=parameters)
    #
    # except Route.DoesNotExist:
    #     raise NoReverseMatch()

    route_obj = get_route_by_view_name(view_name)
    if route_obj:
        return route_obj.get_absolute_url(parameters=parameters)
    else:
        raise NoReverseMatch()

urlpatterns = [
    re_path(r'(?:(?P<path>.*))?$', router, name='navsy-router'),
]

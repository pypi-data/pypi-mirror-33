# -*- coding: utf-8 -*-

from django.core.cache import cache

from navsy.models import Route


def clear():
    delete_routes()


def delete_routes():
    cache.delete('navsy_routes')


def get_routes():
    routes_list = cache.get('navsy_routes', None)
    if not routes_list:
        routes_list = list(Route.objects.all())
        cache.set('navsy_routes', routes_list)
    return routes_list


def get_route_by_page(page):
    if not page or not page.pk:
        return None
    routes_list = get_routes()
    for route_obj in routes_list:
        if route_obj.regex == '':
            page_obj = route_obj.get_page()
            if page_obj.pk == page.pk:
                return route_obj
    return None


def get_route_by_view_name(view_name):
    if not view_name:
        return None
    routes_list = get_routes()
    for route_obj in routes_list:
        if route_obj.view_name == view_name:
            return route_obj
    return None

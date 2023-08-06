# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseRedirect

from navsy.cache import get_routes
# from navsy.models import Route
from navsy.utils import path_utils, url_utils


def router(request, path=None):

    path, path_redirect = path_utils.fix_path_plus(path)
    if path_redirect:
        return HttpResponseRedirect(url_utils.reverse_url(path))
    # print(path)

    # routes_list = list(Route.objects.all())
    routes_list = get_routes()
    routes_list_sorted = [route_obj for route_obj in routes_list if route_obj.regex == ''] + \
                         [route_obj for route_obj in routes_list if route_obj.regex != '']
    routes_list = routes_list_sorted
    # for route_obj in routes_list:
    #     print(route_obj)

    route_not_found = Http404

    for route_obj in routes_list:
        route_re = route_obj.get_absolute_url_regex()
        route_match = route_re.match(path)
        # print('route match: %s -> %s == %s' % (
        #     True if route_match else False, path, route_re.regex_display, ))

        if route_match:
            route_match_kwargs = route_match.groupdict()
            route_match_keys = list(route_match_kwargs.keys())
            route_match_keys.sort(key=lambda arg: route_re.pattern.find(arg))
            route_match_args = [route_match_kwargs[key]
                                for key in route_match_keys]
            # print(route_match_kwargs)
            # print(route_match_keys)
            # print(route_match_args)

            try:
                route_response = route_obj.get_response(
                    request, *route_match_args, **route_match_kwargs)
                return route_response

            except Http404 as route_not_found:
                continue

    raise route_not_found

# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import threading

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.djangoinst.compatability import get_route_handler, \
     get_url_patterns, isDjango20
from tcell_agent.sanitize.sanitize_utils import python_dependent_hash
from tcell_agent.tcell_logger import get_module_logger

ROUTE_TABLE = {}


def get_route_table():
    return ROUTE_TABLE


def get_resolver_match(request):
    if hasattr(request, 'resolver_match') and request.resolver_match:
        return request.resolver_match

    return get_route_handler(request.path_info)


def get_route_id(request):
    resolver_match = get_resolver_match(request)
    if resolver_match:
        return ROUTE_TABLE.get(resolver_match.func, {}).get("route_id")

    return None


def calculate_route_id(uri):
    return str(python_dependent_hash(uri))


def get_route_target(callback):
    route_target = "unknown"
    try:
        if hasattr(callback, '__name__'):
            route_target = callback.__module__ + "." + callback.__name__
        else:
            route_target = callback.__module__ + "." + callback.__class__.__name__
    except Exception as target_exception:
        LOGGER = get_module_logger(__name__)
        LOGGER.error("Exception creating route target: {}".format(target_exception))
        LOGGER.debug(target_exception, exc_info=True)

    return route_target


def clean_regex_pattern(regex_pattern):
    if regex_pattern.startswith("^"):
        regex_pattern = regex_pattern[1:]
    if regex_pattern.endswith("$"):
        regex_pattern = regex_pattern[:-1]

    return regex_pattern


def get_route_url(prefix, pattern):
    if pattern.__class__.__name__ == 'RegexPattern':
        return prefix + clean_regex_pattern(pattern._regex)

    # it's a RoutePattern class
    return prefix + pattern._route


def make_route_table():
    LOGGER = get_module_logger(__name__)

    # django2+ uses URLResolver and URLPattern,
    # RegexURLResolver and RegexURLPattern are used
    # by earlier versions.
    #
    # django 1.5 - 1.9
    # django.core.urlresolvers.RegexURLResolver
    # django.core.urlresolvers.RegexURLPattern
    #
    # django 1.10 - 1.11
    # django.urls.resolvers.RegexURLResolver
    # django.urls.resolvers.RegexURLPattern
    #
    # django 2.0
    # django.urls.resolvers.URLResolver
    # django.urls.resolvers.URLPattern
    def populate_route_table(urllist, prefix=""):
        for entry in urllist:
            try:
                if isDjango20:
                    route_url = get_route_url(prefix, entry.pattern)
                else:
                    route_url = prefix + clean_regex_pattern(entry.regex.pattern)
                route_callback = entry.callback

                if entry.__class__.__name__ == 'RegexURLResolver' or \
                   entry.__class__.__name__ == 'URLResolver':
                    populate_route_table(entry.url_patterns, route_url)
                elif route_callback and (entry.__class__.__name__ == 'RegexURLPattern' or
                                         entry.__class__.__name__ == 'URLPattern'):
                    route_target = get_route_target(route_callback)
                    route_id = calculate_route_id(route_url)
                    ROUTE_TABLE[route_callback] = {"pattern": route_url,
                                                   "target": route_target,
                                                   "route_id": route_id}
            except Exception as add_route_exception:
                LOGGER.error("Exception parsing route {e}".format(e=add_route_exception))
                LOGGER.debug(add_route_exception, exc_info=True)

    def send_route_table():
        try:
            for route_key in ROUTE_TABLE:
                route = ROUTE_TABLE[route_key]
                TCellAgent.discover_route(
                    route.get("pattern"),
                    "*",
                    route.get("target"),
                    route.get("route_id")
                )
        except Exception as exception:
            LOGGER.error("Exception sending route table {e}".format(e=exception))
            LOGGER.debug(exception, exc_info=True)

    try:
        populate_route_table(get_url_patterns())

        send_route_table_thread = threading.Thread(target=send_route_table, args=())
        send_route_table_thread.daemon = True  # Daemonize thread
        send_route_table_thread.start()
    except Exception as exception:
        LOGGER.error("Exception making the route table {e}".format(e=exception))
        LOGGER.debug(exception, exc_info=True)

    return get_route_table

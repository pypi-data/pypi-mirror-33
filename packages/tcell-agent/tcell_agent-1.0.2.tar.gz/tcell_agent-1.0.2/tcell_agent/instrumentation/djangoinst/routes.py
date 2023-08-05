# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import threading

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.djangoinst.utils import midVersionGreaterThanOrEqualTo
from tcell_agent.sanitize.sanitize_utils import python_dependent_hash
from tcell_agent.tcell_logger import get_module_logger

ROUTE_TABLE = {}


def get_route_table():
    return ROUTE_TABLE


def calculate_route_id(uri):
    return str(python_dependent_hash(uri))


def make_route_table():
    LOGGER = get_module_logger(__name__)

    def show_urls(urllist, prefix=""):
        for entry in urllist:
            try:
                pattern = entry.regex.pattern
                if pattern is None:
                    continue
                if pattern.startswith("^"):
                    pattern = pattern[1:]
                if pattern.endswith("$"):
                    pattern = pattern[:-1]
                if entry.__class__.__name__ == 'RegexURLPattern':
                    if entry.callback:
                        route_url = prefix + pattern
                        route_target = "unknown"
                        try:
                            if hasattr(entry.callback, '__name__'):
                                route_target = entry.callback.__module__ + "." + entry.callback.__name__
                            else:
                                route_target = entry.callback.__module__ + "." + entry.callback.__class__.__name__
                        except Exception as target_exception:
                            LOGGER.debug("Exception creating target")
                            LOGGER.debug(target_exception, exc_info=True)
                        route_id = calculate_route_id(route_url)
                        ROUTE_TABLE[entry.callback] = {"pattern": route_url,
                                                       "target": route_target,
                                                       "route_id": route_id}
                if hasattr(entry, 'url_patterns'):
                    show_urls(entry.url_patterns, prefix + pattern)
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
        if midVersionGreaterThanOrEqualTo("1.10"):
            from django.urls.resolvers import get_resolver  # pylint: disable=no-name-in-module
            resolver = get_resolver()
            show_urls(resolver.url_patterns)
        else:
            from django.core.urlresolvers import get_resolver
            resolver = get_resolver(None)
            show_urls(resolver.url_patterns)

        send_route_table_thread = threading.Thread(target=send_route_table, args=())
        send_route_table_thread.daemon = True  # Daemonize thread
        send_route_table_thread.start()
    except Exception as exception:
        LOGGER.error("Exception making the route table {e}".format(e=exception))
        LOGGER.debug(exception, exc_info=True)

    return get_route_table

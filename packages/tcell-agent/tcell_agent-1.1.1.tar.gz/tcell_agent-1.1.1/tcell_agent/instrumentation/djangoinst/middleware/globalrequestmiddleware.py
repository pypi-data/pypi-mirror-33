# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import uuid

import threading

from django import get_version
from django.http import HttpResponse, HttpResponseForbidden

from django.conf import settings

import tcell_agent
from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.django import django_meta, set_request
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.djangoinst.routes import get_route_id
from tcell_agent.instrumentation.djangoinst.settings import send_django_setting_events
from tcell_agent.sensor_events.server_agent_details import ServerAgentDetailsEvent
from tcell_agent.tcell_logger import get_module_logger
from tcell_agent.features.headers import add_headers


def assign_route_id(request):
    request._tcell_context.route_id = get_route_id(request)


def initialize_request(request):
    request._tcell_context.transaction_id = str(uuid.uuid4())
    request._tcell_context.user_agent = request.META.get("HTTP_USER_AGENT")
    request._tcell_context.remote_address = better_ip_address(request.META)
    request._tcell_context.method = request.method


def set_fullpath_and_uri(request):
    request._tcell_context.path = request.path
    request._tcell_context.fullpath = request.get_full_path()
    request._tcell_context.uri = request.build_absolute_uri()


def run_filters(request, response):
    if isinstance(response, HttpResponse):
        response.content = request._tcell_context.filter_body(response.content)


def django_add_headers(request, response):
    if isinstance(response, HttpResponse) and response.has_header("Content-Type"):
        if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
            add_headers(response, request._tcell_context)


def check_location_redirect(request, response):
    redirect_policy = TCellAgent.get_policy(PolicyTypes.HTTP_REDIRECT)

    if redirect_policy and response.get("location"):
        response["location"] = redirect_policy.process_location(
            request._tcell_context.remote_address,
            request.method,
            request.get_host(),
            request.get_full_path(),
            response.status_code,
            response.get("location"),
            user_id=request._tcell_context.user_id,
            session_id=request._tcell_context.session_id,
            route_id=request._tcell_context.route_id)


AGENT_STARTED_LOCK = threading.Lock()


def ensure_agent_started():
    AGENT_STARTED_LOCK.acquire()
    if tcell_agent.instrumentation.djangoinst.app._started:
        AGENT_STARTED_LOCK.release()
        return

    else:
        tcell_agent.instrumentation.djangoinst.app._started = True
        AGENT_STARTED_LOCK.release()

    get_module_logger(__name__).info("Starting agent")

    TCellAgent.get_agent().ensure_polling_thread_running()

    sade = ServerAgentDetailsEvent(framework="Django", framework_version=get_version())
    TCellAgent.send(sade)
    send_django_setting_events()

    if settings.DEFAULT_CHARSET:
        tcell_agent.instrumentation.djangoinst.app._default_charset = settings.DEFAULT_CHARSET


def check_patches_blocking(request):
    rust_policies = TCellAgent.get_policy(PolicyTypes.RUST)
    if rust_policies and rust_policies.patches_enabled:
        appsensor_meta = django_meta(request)
        set_request(appsensor_meta, request)

        if rust_policies.block_request(appsensor_meta):
            request._tcell_context.ip_blocking_triggered = True
            return HttpResponseForbidden()

    return None


class GlobalRequestMiddleware(object):
    _threadmap = {}

    def __init__(self, get_response=None):
        self.get_response = get_response

    # With respect to patches blocking, if a request should be blocked, an
    # HttpResponseForbidden needs to be return during the request phase
    # of the Django middleware.
    #
    # Appropriately returning an http response during the request phase
    # differs depending on Django's version as follows:
    #
    # __call__ method only exists in Django 1.10+ and is the only one that can
    # return an http response for Django 1.10+. Returning an http response
    # from process_request in Django 1.10+ will do nothing
    #
    # For Django < 1.10, process_request is the method in charge of returning
    # an http response, so returning an http response there will be
    # respected (__call__ method never gets called in Django < 1.10)
    #
    # This is the reason why both __call__ and process_request return a
    # block_response when appropriate
    def __call__(self, request):
        block_response = self.process_request(request)

        if block_response:
            return block_response
        else:
            response = self.get_response(request)

            return self.process_response(request, response)

    @classmethod
    def get_current_request(cls):
        try:
            return cls._threadmap[threading.current_thread().ident]
        except Exception:
            pass

    def process_request(self, request):
        if not tcell_agent.instrumentation.djangoinst.app._started:
            ensure_agent_started()

        request._tcell_signals = {}

        request._tcell_context = TCellInstrumentationContext()

        safe_wrap_function("Setting Transaction Id", initialize_request, request)
        safe_wrap_function("Setting Request FullPath", set_fullpath_and_uri, request)
        safe_wrap_function("Assiging route ID to request (global)", assign_route_id, request)

        self._threadmap[threading.current_thread().ident] = request

        block_response = safe_wrap_function(
            "Checking for block rules",
            check_patches_blocking,
            request)

        if block_response:
            return block_response
        else:
            return None

    def process_exception(self, _request, _exception):
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass

    def process_response(self, request, response):
        safe_wrap_function("Check Location Header", check_location_redirect, request, response)
        safe_wrap_function("Insert Headers", django_add_headers, request, response)
        safe_wrap_function("Running Filters", run_filters, request, response)
        try:
            del self._threadmap[threading.current_thread().ident]
        except KeyError:
            pass
        return response

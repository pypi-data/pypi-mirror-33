# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import re

from django.http import HttpResponse

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation import safe_wrap_function


def add_tag(request, response):
    if isinstance(response, HttpResponse) and response.has_header("Content-Type"):
        if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
            rust_policies = TCellAgent.get_policy(PolicyTypes.RUST)
            if rust_policies:
                script_tag = rust_policies.get_js_agent_script_tag(request._tcell_context)
                if script_tag:
                    script_tag = "\g<m>{}".format(script_tag)  # noqa pylint: disable=anomalous-backslash-in-string
                    if not isinstance(response.content, str):
                        script_tag = script_tag.encode("utf-8")

                    response_type = type(response.content)
                    try:
                        if response_type == str:
                            response.content = re.sub(b"(?P<m><head>|<head .+?>)", script_tag, response.content.decode('utf8'))

                        else:
                            response.content = re.sub(b"(?P<m><head>|<head .+?>)", script_tag, response.content)
                    except UnicodeDecodeError:
                        pass


class BodyFilterMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return self.process_response(request, response)

    def process_response(self, request, response):  # pylint: disable=no-self-use
        safe_wrap_function("Insert Body Tag", add_tag, request, response)
        return response

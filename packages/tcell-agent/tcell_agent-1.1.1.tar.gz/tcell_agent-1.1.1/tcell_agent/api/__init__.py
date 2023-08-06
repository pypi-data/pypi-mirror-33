# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

###
# API Module handles all calls to/from the tCell service. Errors are
# handled gracefully since it's generally running silently and should
# fail open.
###

from __future__ import unicode_literals

import json
import requests

from tcell_agent.utils.compat import a_string
from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.version import VERSION
from tcell_agent.tcell_logger import get_module_logger


class SetEncoder(json.JSONEncoder):

    def default(self, o):  # pylint: disable=method-hidden
        if isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)

    def encode(self, o):
        def traverse(o):
            if isinstance(o, dict):
                return {k: traverse(v) for k, v in o.items()}
            elif isinstance(o, list):
                return [traverse(elem) for elem in o]
            elif a_string(o) and (len(o) > 256):
                return o[:256]
            else:
                return o  # no container, just values (str, int, float)
        return super(SetEncoder, self).encode(traverse(o))


class TCellAPIException(Exception):
    # Special API Exception
    pass


class TCellAPI(object):
    @classmethod
    def v1update(cls, last_id=None):
        LOGGER = get_module_logger(__name__)
        url = '{url}/agents/api/v1/apps/{appname}/policies/latest'.format(
            url=CONFIGURATION.tcell_api_url,
            appname=CONFIGURATION.app_id)
        LOGGER.debug("calling api: %s", url)
        params = {
            "type": [
                "jsagentinjection:v1",
                "http-redirect:v1",
                "clickjacking:v1",
                "secure-headers:v1",
                "cmdi:v1",
                "csp-headers:v1",
                "dlp:v1",
                "login:v1",
                "regex:v1",
                "appsensor:v2",
                "patches:v1"]
        }
        if last_id:
            params["last_id"] = last_id
        headers = {"Authorization": "Bearer " + CONFIGURATION.api_key,
                   "TCellAgent": "Python " + VERSION}

        try:
            response = requests.get(url, params=params, headers=headers, allow_redirects=False)
        except Exception as general_exception:
            LOGGER.error("Error connecting to tcell: {e}".format(e=general_exception))
            LOGGER.debug(general_exception, exc_info=True)
            raise TCellAPIException("could not connect to server")

        LOGGER.debug("Policy Response: %s", response)

        if response.ok:
            try:
                result = response.json()
                LOGGER.debug("Policy: %s", result)
                return result
            except Exception as general_exception:
                LOGGER.error("Error parsing tcell response: {e}".format(e=general_exception))
                LOGGER.debug(general_exception, exc_info=True)
                raise TCellAPIException("Error parsing tcell response")

        raise TCellAPIException("Response was not 'ok'")

    @classmethod
    def v1send_events(cls, events):
        LOGGER = get_module_logger(__name__)
        event_endpoint = "server_agent"
        url = '{url}/app/{appname}/{endpoint}'.format(
            url=CONFIGURATION.tcell_input_url,
            appname=CONFIGURATION.app_id,
            endpoint=event_endpoint)
        payload = {"hostname": CONFIGURATION.host_identifier,
                   "uuid": CONFIGURATION.uuid,
                   "events": events}
        LOGGER.debug("sending events to %s", url)
        LOGGER.debug(json.dumps(payload, cls=SetEncoder))
        headers = {"Authorization": "Bearer " + CONFIGURATION.api_key,
                   "Content-type": "application/json",
                   "TCellAgent": "Python " + VERSION}
        response = requests.post(url,
                                 data=json.dumps(payload, cls=SetEncoder),
                                 headers=headers,
                                 allow_redirects=False)
        LOGGER.debug("send_events response: [%s]", response.status_code)
        return response.status_code

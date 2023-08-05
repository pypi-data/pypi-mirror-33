import unittest

from collections import namedtuple
from mock import call, patch

from django.utils.datastructures import MultiValueDict

from tcell_agent.agent import TCellAgent
from tcell_agent.appsensor.django import set_request
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.rust_policies import RustPolicies

FakeFile = namedtuple("FakeFile", ["name"], verbose=True)
FakeRequest = namedtuple("FakeRequest", ["body", "META", "GET", "POST", "FILES", "COOKIES", "environ"], verbose=True)
FakeResponse = namedtuple("FakeResponse", ["content", "status_code"], verbose=True)

regex_policy = {
    "data": {
        "patterns": [
            {
                "id": "tc-xss-1",
                "pattern": "(?:<(script))",
                "sensor": "xss",
                "title": "Basic Injection"
            }
        ],
        "version": 1518546622571
    },
    "policy_id": "f3a313b0-10eb-11e8-8080-808080808080",
    "version": 1
}


class AppSensorPolicyCheckParamsTest(unittest.TestCase):
    def uploading_zero_file_test(self):
        policy = RustPolicies()
        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)
            self.assertFalse(patched_send.called)

    def uploading_one_file_test(self):  # pylint: disable=no-self-use
        policy_one = {
            "regex": regex_policy,
            "appsensor": {
                "policy_id": "nyzd",
                "version": 2,
                "data": {
                    "options": {
                        "payloads": {
                            "send_payloads": False,
                            "log_payloads": False
                        }
                    },
                    "sensors": {
                        "xss": {
                            "dynamic_patterns": ["tc-xss-1"],
                            "patterns": ["1"]
                        }
                    }
                }
            }
        }

        policy = RustPolicies()
        policy.load_from_json(policy_one)
        files_dict = MultiValueDict({"avatar": [FakeFile("<script>alert()</script>")]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            patched_send.assert_called_once_with({
                "event_type": "as",
                "remote_addr": "remote_addr",
                "pattern": "tc-xss-1",
                "m": "request_method",
                "uri": "abosolute_uri",
                "param": "avatar",
                "meta": {"l": "body"},
                "sid": "session_id",
                "rid": "route_id",
                "dp": "xss",
                "uid": "user_id"})

    def uploading_two_files_for_same_param_test(self):  # pylint: disable=no-self-use
        policy_one = {
            "regex": regex_policy,
            "appsensor": {
                "policy_id": "nyzd",
                "version": 2,
                "data": {
                    "options": {
                        "payloads": {
                            "send_payloads": False,
                            "log_payloads": False
                        }
                    },
                    "sensors": {
                        "xss": {
                            "dynamic_patterns": ["tc-xss-1"],
                            "patterns": ["1"]
                        }
                    }
                }
            }
        }
        policy = RustPolicies()
        policy.load_from_json(policy_one)

        files_dict = MultiValueDict({
            "avatar": [FakeFile("<script>alert()</script>"), FakeFile("<script></script>")]
        })
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "pattern": "tc-xss-1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"}),
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "pattern": "tc-xss-1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"
                        })
                ],
                True
            )

    def collect_uri_version_one_uploading_two_files_for_different_params_test(self):  # pylint: disable=no-self-use
        policy_one = {
            "regex": regex_policy,
            "appsensor": {
                "policy_id": "nyzd",
                "version": 2,
                "data": {
                    "options": {
                        "payloads": {
                            "send_payloads": False,
                            "log_payloads": False
                        },
                        "uri_options": {
                            "collect_full_uri": True
                        }
                    },
                    "sensors": {
                        "xss": {
                            "dynamic_patterns": ["tc-xss-1"],
                            "patterns": ["1"]
                        }
                    }
                }
            }
        }
        policy = RustPolicies()
        policy.load_from_json(policy_one)

        files_dict = MultiValueDict({
            "avatar": [FakeFile("<script>alert()</script>")],
            "picture": [FakeFile("<script>alert()</script>")]
        })
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("",
                              {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"},
                              {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "pattern": "tc-xss-1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"}),
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "pattern": "tc-xss-1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "picture",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"})
                ],
                True
            )

    def collect_uri_version_two_uploading_two_files_for_different_params_test(self):  # pylint: disable=no-self-use
        policy_one = {
            "regex": regex_policy,
            "appsensor": {
                "policy_id": "nyzd",
                "version": 2,
                "data": {
                    "options": {
                        "payloads": {
                            "send_payloads": False,
                            "log_payloads": False
                        },
                        "uri_options": {
                            "collect_full_uri": True
                        }
                    },
                    "sensors": {
                        "xss": {
                            "dynamic_patterns": ["tc-xss-1"],
                            "patterns": ["1"]
                        }
                    }
                }
            }
        }
        policy = RustPolicies()
        policy.load_from_json(policy_one)

        files_dict = MultiValueDict({
            "avatar": [FakeFile("<script>alert()</script>")],
            "picture": [FakeFile("<script>alert()</script>")]
        })
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(TCellAgent, "send", return_value=None) as patched_send:
            policy.check_appfirewall_injections(appsensor_meta)

            patched_send.assert_has_calls(
                [
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "pattern": "tc-xss-1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "avatar",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"}),
                    call({
                        "event_type": "as",
                        "remote_addr": "remote_addr",
                        "pattern": "tc-xss-1",
                        "m": "request_method",
                        "uri": "abosolute_uri",
                        "param": "picture",
                        "meta": {"l": "body"},
                        "sid": "session_id",
                        "full_uri": "abosolute_uri",
                        "rid": "route_id",
                        "dp": "xss",
                        "uid": "user_id"})
                ],
                True
            )

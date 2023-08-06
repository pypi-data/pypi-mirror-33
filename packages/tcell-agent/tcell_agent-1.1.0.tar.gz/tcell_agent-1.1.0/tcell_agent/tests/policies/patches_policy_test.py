import unittest

from collections import namedtuple

from django.utils.datastructures import MultiValueDict

from tcell_agent.appsensor.django import set_request
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.policies.rust_policies import RustPolicies
from tcell_agent.rust.whisperer import free_agent

FakeFile = namedtuple("FakeFile", ["name"], verbose=True)
FakeRequest = namedtuple("FakeRequest", ["body", "META", "GET", "POST", "FILES", "COOKIES", "environ"], verbose=True)
FakeResponse = namedtuple("FakeResponse", ["content", "status_code"], verbose=True)


class PatchesPolicyTest(unittest.TestCase):
    def setUp(self):
        old_app_id = CONFIGURATION.app_id
        old_api_key = CONFIGURATION.api_key
        old_js_agent_api_base_url = CONFIGURATION.js_agent_api_base_url
        old_js_agent_url = CONFIGURATION.js_agent_url

        CONFIGURATION.app_id = "app_id"
        CONFIGURATION.api_key = "api_key"
        CONFIGURATION.js_agent_api_base_url = "http://api.tcell.com/"
        CONFIGURATION.js_agent_url = "https://jsagent.tcell.io/tcellagent.min.js"

        self.policy = RustPolicies()

        CONFIGURATION.app_id = old_app_id
        CONFIGURATION.api_key = old_api_key
        CONFIGURATION.js_agent_api_base_url = old_js_agent_api_base_url
        CONFIGURATION.js_agent_url = old_js_agent_url

    def tearDown(self):
        free_agent(self.policy.agent_ptr)

    def classname_test(self):
        self.assertEqual(RustPolicies.patches_identifier, "patches")

    def none_policy_test(self):
        self.assertIsNotNone(self.policy.agent_ptr)
        self.assertFalse(self.policy.patches_enabled)

    def empty_version_policy_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id"
            }
        })

        self.assertIsNotNone(self.policy.agent_ptr)
        self.assertFalse(self.policy.patches_enabled)

    def empty_data_policy_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {}
            }
        })

        self.assertIsNotNone(self.policy.agent_ptr)
        self.assertTrue(self.policy.patches_enabled)

    def populated_blocked_ips_policy_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "blocked_ips": [{
                        "ip": "1.1.1.1"
                    }]
                }
            }
        })

        self.assertIsNotNone(self.policy.agent_ptr)
        self.assertTrue(self.policy.patches_enabled)

    def populated_blocked_ips_with_wrong_version_policy_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "blocked_ips": [{
                        "ip": "1.1.1.1"
                    }]
                }
            }
        })

        self.assertIsNotNone(self.policy.agent_ptr)
        self.assertTrue(self.policy.patches_enabled)

    def populated_blocked_ips_with_missing_ip_policy_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "blocked_ips": [{
                        "ip_wrong": "1.1.1.1"
                    }]
                }
            }
        })

        self.assertIsNotNone(self.policy.agent_ptr)
        self.assertTrue(self.policy.patches_enabled)

    def disabled_ip_blocking_block_request_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                }
            }
        })

        meta_data = {}

        self.assertFalse(self.policy.block_request(meta_data))

    def enabled_ip_blocking_block_request_with_none_ip_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = None
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

        self.assertFalse(self.policy.block_request(appsensor_meta))

    def enabled_ip_blocking_block_request_with_empty_ip_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = ""
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        self.assertFalse(self.policy.block_request(appsensor_meta))

    def enabled_ip_blocking_block_request_with_blocked_ip_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "1.1.1.1"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        self.assertTrue(self.policy.block_request(appsensor_meta))

    def enabled_ip_blocking_block_request_with_non_blocked_ip_test(self):
        self.policy.load_from_json({
            "patches": {
                "policy_id": "policy_id",
                "version": 2,
                "data": {
                    "rules": [{
                        "id": "blocked-ips-rule",
                        "title": "Blocked ips rule",
                        "action": "BlockIf",
                        "destinations": {"check_equals": [{"path": "*"}]},
                        "ignore": [],
                        "matches": [{
                            "all": [],
                            "any": [{
                                "ips": [{
                                    "type": "IP",
                                    "values": ["1.1.1.1"]
                                }]
                            }]
                        }]
                    }]
                }
            }
        })

        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "2.2.2.2"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest("", {"CONTENT_LENGTH": 1024, "HTTP_USER_AGENT": "user_agent"}, {}, {}, files_dict, {}, {})
        response = FakeResponse("AA", 200)
        set_request(appsensor_meta, request)
        appsensor_meta.set_response(type(response), response)

        self.assertFalse(self.policy.block_request(appsensor_meta))

import unittest

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.policies.rust_policies import RustPolicies
from tcell_agent.rust.whisperer import free_agent


class ContentSecurityPolicyTest(unittest.TestCase):
    def setUp(self):
        old_app_id = CONFIGURATION.app_id
        old_api_key = CONFIGURATION.api_key
        old_js_agent_api_base_url = CONFIGURATION.js_agent_api_base_url
        old_js_agent_url = CONFIGURATION.js_agent_url
        old_max_csp_header_bytes = CONFIGURATION.max_csp_header_bytes

        CONFIGURATION.app_id = "app_id"
        CONFIGURATION.api_key = "api_key"
        CONFIGURATION.js_agent_api_base_url = "http://api.tcell.com/"
        CONFIGURATION.js_agent_url = "https://jsagent.tcell.io/tcellagent.min.js"
        CONFIGURATION.max_csp_header_bytes = 55

        self.policy = RustPolicies()

        CONFIGURATION.app_id = old_app_id
        CONFIGURATION.api_key = old_api_key
        CONFIGURATION.js_agent_api_base_url = old_js_agent_api_base_url
        CONFIGURATION.js_agent_url = old_js_agent_url
        CONFIGURATION.max_csp_header_bytes = old_max_csp_header_bytes

        self.tcell_context = TCellInstrumentationContext()
        self.tcell_context.path = "GET"
        self.tcell_context.method = "/"

    def tearDown(self):
        free_agent(self.policy.agent_ptr)

    def new_header_test(self):
        policy_json = {
            "csp-headers": {
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "test321"}]}}

        self.policy.load_from_json(policy_json)
        self.assertEqual(self.policy.get_headers(self.tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "test321"}])

    def header_with_report_uri_test(self):
        policy_json = {
            "csp-headers": {
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "normalvalue",
                             "report_uri": "https://www.example.com/xys"}]}}
        self.policy.load_from_json(policy_json)
        self.assertEqual(self.policy.get_headers(self.tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "normalvalue; report-uri https://www.example.com/xys"}])

    def header_equal_to_max_csp_header_bytes_test(self):
        policy_json = {
            "csp-headers": {
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "normalvalue",
                             "report_uri": "https://www.example.com/1234567"}]}}

        self.policy.load_from_json(policy_json)
        self.assertEqual(self.policy.get_headers(self.tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "normalvalue; report-uri https://www.example.com/1234567"}])

    def header_exceeding_max_csp_header_bytes_test(self):
        policy_json = {
            "csp-headers": {
                "policy_id": "xyzd",
                "headers": [{"name": "Content-Security-Policy",
                             "value": "normalvalue",
                             "report_uri": "https://www.example.com/12345678"}]}}
        self.policy.load_from_json(policy_json)
        # no headers returned because they are bigger than max_csp_header_bytes
        self.assertEqual(self.policy.get_headers(self.tcell_context), [])

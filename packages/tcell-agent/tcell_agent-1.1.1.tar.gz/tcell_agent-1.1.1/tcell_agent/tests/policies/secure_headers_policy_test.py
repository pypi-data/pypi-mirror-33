import unittest

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.policies.rust_policies import RustPolicies
from tcell_agent.rust.whisperer import free_agent


class SecureHeaderPolicyTest(unittest.TestCase):
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

        self.tcell_context = TCellInstrumentationContext()
        self.tcell_context.path = "GET"
        self.tcell_context.method = "/"

    def tearDown(self):
        free_agent(self.policy.agent_ptr)

    def one_header_test(self):
        policy_json = {
            "secure-headers": {
                "policy_id": "xyzd",
                "headers": [{"name": "X-Content-Type-Options",
                             "value": "nosniff"}]}}
        self.policy.load_from_json(policy_json)
        self.assertEqual(self.policy.get_headers(self.tcell_context),
                         [{"name": "X-Content-Type-Options", "value": "nosniff"}])

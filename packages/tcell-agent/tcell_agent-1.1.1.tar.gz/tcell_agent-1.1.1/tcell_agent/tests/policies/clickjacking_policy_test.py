import unittest

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.policies.rust_policies import RustPolicies
from tcell_agent.rust.whisperer import free_agent


class ClickjackingPolicyTest(unittest.TestCase):
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

    def new_header_test(self):
        policy_json = {
            "clickjacking": {
                "policy_id": "890f1310-5c6c-11e8-8080-808080808080",
                "headers": [
                    {
                        "name": "Content-Security-Policy",
                        "value": "frame-ancestors 'none'",
                        "report_uri": "https://input.tcell-preview.io/csp/430d"
                    }
                ],
                "version": 1
            }
        }
        tcell_context = TCellInstrumentationContext()
        tcell_context.path = "GET"
        tcell_context.method = "/"
        self.policy.load_from_json(policy_json)
        self.assertEqual(self.policy.get_headers(tcell_context),
                         [{"name": "Content-Security-Policy",
                           "value": "frame-ancestors 'none'; report-uri https://input.tcell-preview.io/csp/430d"}])

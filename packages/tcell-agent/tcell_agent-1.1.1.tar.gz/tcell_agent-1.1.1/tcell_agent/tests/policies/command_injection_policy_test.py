import unittest

from mock import patch

from tcell_agent.agent import TCellAgent
from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.policies.rust_policies import RustPolicies
from tcell_agent.rust.whisperer import free_agent


class CommandInjectionPolicyTest(unittest.TestCase):
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
        self.assertEqual(RustPolicies.cmdi_identifier, "cmdi")

    def blank_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": []}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def ignore_all_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [{"rule_id": "1", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def block_all_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "collect_full_commandline": True,
                    "command_rules": [{"rule_id": "1", "action": "block"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "1"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True,
                    "full_commandline": "cat /etc/passwd && grep root"
                })

    def ignore_all_ignore_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "collect_full_commandline": True,
                    "command_rules": [
                        {"rule_id": "1", "action": "ignore"},
                        {"rule_id": "2", "action": "ignore", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def ignore_all_report_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "ignore"},
                        {"rule_id": "2", "action": "report", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def ignore_all_block_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "ignore"},
                        {"rule_id": "2", "action": "block", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def report_all_ignore_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "report"},
                        {"rule_id": "2", "action": "ignore", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def report_all_report_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "report"},
                        {"rule_id": "2", "action": "report", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def report_all_block_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "report"},
                        {"rule_id": "2", "action": "block", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def block_all_ignore_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "block"},
                        {"rule_id": "2", "action": "ignore", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def block_all_report_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "block"},
                        {"rule_id": "2", "action": "report", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def block_all_block_cat_command_rules_block_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "command_rules": [
                        {"rule_id": "1", "action": "block"},
                        {"rule_id": "2", "action": "block", "command": "cat"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"command": "cat", "rule_id": "2"}, {"command": "grep", "rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def ignore_one_command_compound_statement_rules_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd", None))
                self.assertFalse(patched_send.called)

    def ignore_two_command_compound_statement_rules_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                self.assertFalse(patched_send.called)

    def report_one_command_compound_statement_rules_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "report"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd", None))
                self.assertFalse(patched_send.called)

    def report_two_command_compound_statement_rules_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "report"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": False
                })

    def block_one_command_compound_statement_rules_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "block"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertFalse(self.policy.block_command("cat /etc/passwd", None))
                self.assertFalse(patched_send.called)

    def block_two_command_compound_statement_rules_test(self):
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "block"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

    def multiple_compound_statemetns_block_two_command_compound_statement_rules_test(self):
        # multiple compound statements present only first one is taken
        self.policy.load_from_json(
            {"cmdi": {
                "policy_id": "policy_id",
                "version": 1,
                "data": {
                    "compound_statement_rules": [
                        {"rule_id": "1", "action": "block"}, {"rule_id": "2", "action": "ignore"}]}}})

        with patch.object(TCellAgent, "is_it_safe_to_send_cmdi_events", return_value=True):
            with patch.object(TCellAgent, "send", return_value=None) as patched_send:
                self.assertTrue(self.policy.block_command("cat /etc/passwd && grep root", None))
                patched_send.assert_called_once_with({
                    "event_type": "cmdi",
                    "matches": [{"rule_id": "1"}],
                    "commands": [{"arg_count": 1, "command": "cat"}, {"arg_count": 1, "command": "grep"}],
                    "blocked": True
                })

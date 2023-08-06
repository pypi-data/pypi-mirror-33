import re

from tcell_agent.agent import TCellAgent, PolicyTypes


def insert_js_agent(request, response):
    if not response.is_streamed and response.headers.get("Content-Type", None) \
       and response.headers["Content-Type"].startswith("text/html"):
        rust_policies = TCellAgent.get_policy(PolicyTypes.RUST)
        if rust_policies:
            script_tag = rust_policies.get_js_agent_script_tag(request._tcell_context)
            if script_tag:
                script_tag = "\g<m>{}".format(script_tag)  # noqa pylint: disable=anomalous-backslash-in-string
                response_content = response.get_data(True)
                response_content = re.sub("(?P<m><head>|<head .+?>)", script_tag, response_content)
                from flask.wrappers import Response
                response = Response(response_content, status=response.status_code, headers=response.headers)

    return response

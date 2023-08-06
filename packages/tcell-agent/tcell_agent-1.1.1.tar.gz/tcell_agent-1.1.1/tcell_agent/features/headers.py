from tcell_agent.agent import TCellAgent, PolicyTypes


def add_headers(headers, tcell_context):
    rust_policies = TCellAgent.get_policy(PolicyTypes.RUST)
    if rust_policies:
        tcell_headers = rust_policies.get_headers(tcell_context)
        for header_info in tcell_headers:
            header_name = header_info['name']
            header_value = header_info['value']
            existing_header_value = headers.get(header_name)
            if existing_header_value:
                headers[header_name] = "{}, {}".format(existing_header_value, header_value)
            else:
                headers[header_name] = header_value

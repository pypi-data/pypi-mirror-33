from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.features.headers import add_headers


def flask_add_headers(request, response):
    if response.headers.get("Content-Type", None) and \
       response.headers["Content-Type"].startswith("text/html"):
        add_headers(response.headers, request._tcell_context)


def check_location_redirect(request, response):
    redirect_policy = TCellAgent.get_policy(PolicyTypes.HTTP_REDIRECT)

    if redirect_policy and response.location:
        meta = request._appsensor_meta
        response.headers['location'] = redirect_policy.process_location(
            better_ip_address(request.environ),
            request.environ.get("REQUEST_METHOD", None),
            request.host,
            request.path,
            response.status_code,
            response.location,
            user_id=meta.user_id,
            session_id=meta.session_id,
            route_id=meta.route_id)

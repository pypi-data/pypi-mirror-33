import unittest

from mock import Mock, patch

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.flaskinst.headers import flask_add_headers, \
     check_location_redirect


class FlaskHeadersTest(unittest.TestCase):

    def flask_add_headers_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.path = "GET"
        tcell_context.method = "/"
        tcell_context.route_id = "route_id"
        tcell_context.session_id = "session_id"

        request = Mock(_tcell_context=tcell_context)
        response = Mock(headers={"Content-Type": "text/html"})

        mock = Mock()
        mock.get_headers = Mock(return_value=[{"name": "Content-Security-Policy",
                                               "value": "normalvalue; report-uri https://www.example.com/xys"}])
        with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
            flask_add_headers(request, response)
            patched_get_policy.assert_called_once_with(PolicyTypes.RUST)
            mock.get_headers.assert_called_once_with(tcell_context)
            self.assertEqual(response.headers,
                             {'Content-Security-Policy': 'normalvalue; report-uri https://www.example.com/xys',
                              'Content-Type': 'text/html'})

    def flask_add_header_with_existing_header_test(self):
        tcell_context = TCellInstrumentationContext()
        tcell_context.path = "GET"
        tcell_context.method = "/"
        tcell_context.route_id = "route_id"
        tcell_context.session_id = "session_id"

        request = Mock(_tcell_context=tcell_context)
        response = Mock(headers={"Content-Type": "text/html",
                                 "Content-Security-Policy": "default-src \"none\""})

        mock = Mock()
        mock.get_headers = Mock(return_value=[{"name": "Content-Security-Policy",
                                               "value": "normalvalue; report-uri https://www.example.com/xys"}])
        with patch.object(TCellAgent, "get_policy", return_value=mock) as patched_get_policy:
            flask_add_headers(request, response)
            patched_get_policy.assert_called_once_with(PolicyTypes.RUST)
            mock.get_headers.assert_called_once_with(tcell_context)
            self.assertEqual(response.headers,
                             {'Content-Security-Policy': 'default-src "none", normalvalue; report-uri https://www.example.com/xys',
                              'Content-Type': 'text/html'})

    def check_location_redirect_test(self):  # pylint: disable=no-self-use
        request = Mock(
            _appsensor_meta=AppSensorMeta(),
            path="/path",
            host="host",

            environ={
                "REMOTE_ADDR": "192.168.1.115",
                "REQUEST_METHOD": "GET"})
        request._appsensor_meta.route_id = "route_id"
        request._appsensor_meta.session_id = "session_id"
        request._appsensor_meta.user_id = "user_id"
        response = Mock(headers={}, location="/redirect", status_code=200)
        redirect_policy = Mock()

        with patch.object(TCellAgent, "get_policy", return_value=redirect_policy) as patched_get_policy:
            check_location_redirect(request, response)

            patched_get_policy.assert_called_once_with(PolicyTypes.HTTP_REDIRECT)
            redirect_policy.process_location.assert_called_once_with(
                "192.168.1.115",
                "GET",
                "host",
                "/path",
                200,
                "/redirect",
                user_id="user_id",
                session_id="session_id",
                route_id="route_id")

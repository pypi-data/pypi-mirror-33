from webapp2 import WSGIApplication
from webtest import TestApp


def create_simple_test_app(routes):
  """Create a simple webtest.TestApp with the specified routes.

  Args:
    routes: list of webapp2.Routes

  Returns:
    webtest.TestApp wrapping a webapp2.WSGIApplication
  """
  return TestApp(
    WSGIApplication(
      routes=routes,
      debug=True,
    )
  )

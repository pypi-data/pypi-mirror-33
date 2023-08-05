import unittest

from google.appengine.ext import testbed
import mock


class SimpleAppEngineTestCase(unittest.TestCase):
  """A very simple AppEngine test case which sets up basic stubs.

  By default, stubs for Datastore and Memcache are created.
  """

  def setUp(self):
    """Override setUp to set up stubs."""
    self.testbed = testbed.Testbed()

    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_urlfetch_stub()

    self.addCleanup(mock.patch.stopall)

  def tearDown(self):
    """Override tearDown to set up stubs."""
    self.testbed.deactivate()


class ServiceAPITestCase(SimpleAppEngineTestCase):
  """Testcase for Service APIs.

  Circumvents the X-AppEngine header check that verifies requests are coming
  from within the application. That functionality is tested in
  catnado.handlers.test.test_csrf_protected_handler.
  """

  def setUp(self):
    """Override setUp to patch over request validation."""
    self._csrf_token_patch = mock.patch(
      'catnado.handlers.service_api_handler.validate_api_request'
    )
    self._csrf_token_mock = self._csrf_token_patch.start()
    super(ServiceAPITestCase, self).setUp()

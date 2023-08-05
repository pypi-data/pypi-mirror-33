from catnado.handlers.simple_public_handler import SimplePublicHandler
from catnado.utils.csrf import get_csrf_token, validate_csrf_token


CSRF_TOKEN = 'csrf_token'


class CSRFProtectedHandler(SimplePublicHandler):
  """SimplePublicHandler that requires a CSRF token on POST."""

  CSRF_PROTECTED_METHODS = {'POST', 'PUT', 'DELETE'}

  def dispatch(self):
    """Override dispatch to CSRF-validate POST requests."""
    if self.request.method in self.CSRF_PROTECTED_METHODS:
      if not validate_csrf_token(self):
        self.abort(403, detail='CSRF protection')

    super(CSRFProtectedHandler, self).dispatch()

  @staticmethod
  def jinja_render(template, kwargs=None):
    """set content-type and write json data in a response.

    arguments:
      kwargs: an optional dict to pass to the jinja template
    """
    kwargs = kwargs or {}
    kwargs[CSRF_TOKEN] = get_csrf_token()
    super(CSRFProtectedHandler, self).jinja_render(template, kwargs)

from catnado.handlers import CatnadoHandler, CONTENT_TYPE, CONTENT_TYPE_HTML
from catnado.utils.jinja import create_jinja_environment


class SimplePublicHandler(CatnadoHandler):
  """Handler for serving a microservice's internal API.

  Ensures that incoming requests are coming from within the same application by
  verifying that the X-Appengine-Inbound-Appid matches the current application's
  ID.
  """

  TEMPLATES_PATH = None

  @property
  def jinja_env(self):
    """Get a Jinja environment for this handler at TEMPLATES_PATH.

    The created Jinja environment is cached on the request for future calls.

    Returns:
      jinja2.Environment with a template directory at TEMPLATES_PATH
    """
    assert self.TEMPLATES_PATH is not None
    if not hasattr(self, '_jinja_env'):
      self._jinja_env = create_jinja_environment(self.TEMPLATES_PATH)
    return self._jinja_env

  @staticmethod
  def jinja_render(template, kwargs=None):
    """Set Content-Type and write JSON data in a response.

    Arguments:
      kwargs: an optional dict to pass to the Jinja template
    """
    kwargs = kwargs or {}
    self.response.headers[CONTENT_TYPE] = CONTENT_TYPE_HTML

    template = self.jinja_env.get_template(template)
    if template:
      self.response.out.write(template.render(**kwargs))

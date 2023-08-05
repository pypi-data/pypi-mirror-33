import logging

from catnado import __VERSION__
from catnado.utils.jinja import create_jinja_environment
from webapp2 import RequestHandler


CONTENT_TYPE = 'Content-Type'
CONTENT_TYPE_HTML = 'text/html'


class StaticPageHandler(RequestHandler):
  """Handler for serving a microservice's internal API.

  Ensures that incoming requests are coming from within the same application by
  verifying that the X-Appengine-Inbound-Appid matches the current application's
  ID.
  """
  TEMPLATES_PATH = None

  @property
  def jinja_env(self):
    assert self.TEMPLATES_PATH is not None
    if not hasattr(self, '_jinja_env'):
      logging.critical('creating jinja environment at {}'.format(self.TEMPLATES_PATH))
      self._jinja_env = create_jinja_environment(self.TEMPLATES_PATH)
    return self._jinja_env

  def jinja_render(self, template, kwargs=None):
    """Set Content-Type and write JSON data in a response.

    Arguments:
      kwargs: an optional dict to pass to the Jinja template
    """
    logging.critical('version {} is rendering!'.format(__VERSION__))

    kwargs = kwargs or {}
    self.response.headers[CONTENT_TYPE] = CONTENT_TYPE_HTML

    template = self.jinja_env.get_template(template)
    if template:
      self.response.out.write(template.render(**kwargs))

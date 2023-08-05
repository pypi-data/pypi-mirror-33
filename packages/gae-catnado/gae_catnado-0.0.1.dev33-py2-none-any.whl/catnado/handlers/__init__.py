import json

from webapp2 import RequestHandler

from catnado.utils.validators import CLEAN_DATA


CONTENT_TYPE = 'Content-Type'
CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_HTML = 'text/html'


class CatnadoHandler(RequestHandler):
  """Base handler for Catnado.

  Provides miscellaneous base functionality.
  """

  @property
  def clean_request_data(self):
    """Get clean request data saved with an @validator."""
    clean_data = self.request.registry.get(CLEAN_DATA, {})
    return clean_data

  def json_response(self, out, code=200):
    """Write an application/json response.

    Args:
      out: dictionary to serialize to JSON and send as a response
      code: optional int; sets the HTTP status code of the response
    """
    self.response.set_status(code)
    self.response.headers[CONTENT_TYPE] = CONTENT_TYPE_JSON
    self.response.out.write(json.dumps(out))

import json


class UrlfetchResponse(object):
  """Fake Response object for urlfetch."""

  def __init__(self, status_code=200, body=None, headers=None):
    """Override constructor.

    Args:
      status_code: optional int; HTTP status code (200)
      body: optional object--will be JSON serialized (None)
      headers: optional dict of headers (None)
    """
    self.status_code = status_code
    self.body = json.dumps(body)
    self.headers = headers

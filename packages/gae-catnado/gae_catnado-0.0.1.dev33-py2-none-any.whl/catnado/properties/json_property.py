import json

from google.appengine.ext import db
import jsonschema


class JSONProperty(db.Property):
  """Property for storing simple JSON objects backed by a schema."""

  data_type = db.Blob

  def __init__(self, schema=None, *args, **kwargs):
    """Constructor.

    Args:
      schema: a JSON Schema per draft 3 or 4 of json-schema.org
    """
    self.schema = schema
    super(JSONProperty, self).__init__(*args, **kwargs)

  def validate(self, value):
    """Validate that the value is valid JSON that conforms to the self.schema.

    Args:
      value: JSON-serializable object
    Returns:
      value, unchanged
    """
    if self.schema:
      try:
        jsonschema.validate(value, self.schema)
      except jsonschema.ValidationError:
        raise db.BadValueError
    return value

  def make_value_from_datastore(self, value):
    """Convert the datastore blob to a Python object."""
    return json.loads(value)

  def get_value_for_datastore(self, model_instance):
    """Convert the Python object value into a string for the datastore."""
    value = self.__get__(model_instance, model_instance.__class__)
    return json.dumps(value)

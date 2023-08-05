"""See http://googleappengine.blogspot.com/2009/07/writing-custom-property-classes.html."""

import decimal

from google.appengine.ext import db


class DecimalProperty(db.Property):
  """Property for storing Decimal types."""

  data_type = decimal.Decimal

  def get_value_for_datastore(self, model_instance):
    """Convert Decimal to str for datastore."""
    return str(super(DecimalProperty, self).get_value_for_datastore(model_instance))

  def make_value_from_datastore(self, value):
    """Convert str from datastore back to Decimal."""
    return decimal.Decimal(value)

  def validate(self, value):
    """Validator.

    Args:
      value: either a string or Decimal
    Returns:
      Decimal
    Raises:
      db.BadValueError: if value is not a Decimal or valid string
    """
    value = super(DecimalProperty, self).validate(value)
    if value is None or isinstance(value, decimal.Decimal):
      return value
    elif isinstance(value, basestring):
      return decimal.Decimal(value)
    raise db.BadValueError("Property %s must be a Decimal or string." % self.name)

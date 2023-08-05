import zlib

from google.appengine.ext import db


class CompressedProperty(db.UnindexedProperty):
  """An unindexed, compressed property.

  CompressedTextProperty and CompressedBlobProperty derive from this class.
  """

  def __init__(self, level, *args, **kwargs):
    """Constructor.

    Args:
      level: Controls the level of zlib's compression (between 1 and 9).
    """
    super(CompressedProperty, self).__init__(*args, **kwargs)
    self.level = level

  def get_value_for_datastore(self, model_instance):
    value = self.value_to_str(model_instance)
    if value is not None:
      return db.Blob(zlib.compress(value, self.level))

  def make_value_from_datastore(self, value):
    if value is not None:
      ds_value = zlib.decompress(value)
      return self.str_to_value(ds_value)

  # override value_to_str and str_to_value to implement a new CompressedProperty
  def value_to_str(self, model_instance):
    """Returns the value stored by this property encoded as a (byte) string,
    or None if value is None.  This string will be stored in the datastore.
    By default, returns the value unchanged."""
    return self.__get__(model_instance, model_instance.__class__)

  @staticmethod
  def str_to_value(s):
    """Reverse of value_to_str.  By default, returns s unchanged."""
    return s


class CompressedBlobProperty(CompressedProperty):
  """A byte string that will be stored in a compressed form.
  """
  data_type = db.Blob

  def __init__(self, level=6, *args, **kwargs):
    super(CompressedBlobProperty, self).__init__(level, *args, **kwargs)


class CompressedTextProperty(CompressedProperty):
  """A string that will be stored in a compressed form (encoded as UTF-8).
  """
  data_type = db.Text

  def __init__(self, level=6, *args, **kwargs):
    super(CompressedTextProperty, self).__init__(level, *args, **kwargs)

  def value_to_str(self, model_instance):
    return self.__get__(model_instance, model_instance.__class__).encode('utf-8')

  @staticmethod
  def str_to_value(s):
    return s.decode('utf-8')

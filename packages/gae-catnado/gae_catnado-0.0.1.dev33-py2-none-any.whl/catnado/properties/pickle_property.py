import copy
import pickle

from google.appengine.ext import db


class PickleProperty(db.Property):
  """Property for storing complex objects in the datastore in pickled form."""

  data_type = db.Blob

  def get_value_for_datastore(self, model_instance):
    """Un-pickle data from the datastore."""
    value = self.__get__(model_instance, model_instance.__class__)
    if value is not None:
      return db.Blob(pickle.dumps(value))

  def make_value_from_datastore(self, value):
    """Pickle data to store it."""
    if value is not None:
      return pickle.loads(str(value))

  def default_value(self):
    """If possible, copy the value passed in the default= keyword argument.

    This prevents mutable objects such as dictionaries from being shared across
    instances.
    """
    return copy.copy(self.default)

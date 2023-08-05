from google.appengine.ext import db


class ImmutablePropertyException(Exception):
  """Raise when someone tries to set an immutable property."""

  pass


class ImmutableMixin(object):
  """Mixin to make a property immutable."""

  def __set__(self, instance, value):

    if hasattr(instance, self._attr_name()):
      raise ImmutablePropertyException('{} is immutable'.format(self.name))

    super(ImmutableMixin, self).__set__(instance, value)


class ImmutableStringProperty(ImmutableMixin, db.StringProperty):
  """An immutable version of `google.appengine.ext.db.StringProperty`."""

  pass

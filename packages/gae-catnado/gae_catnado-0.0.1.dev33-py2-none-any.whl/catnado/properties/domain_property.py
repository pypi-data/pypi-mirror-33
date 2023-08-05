import os

from google.appengine.api import users
from google.appengine.ext import db


class CurrentDomainProperty(db.Property):
  """A property that restricts access to the current domain.
  """

  def __init__(self, allow_read=False, allow_write=False, *args, **kwargs):
    """Constructor.

    Args:
      allow_read: If True, allow entities with this property to be read, but not
        written, from other domains.
      allow_write: If True, allow entities with this property to be modified
        from other domains.
    """
    self.allow_read = allow_read
    self.allow_write = allow_write
    super(CurrentDomainProperty, self).__init__(*args, **kwargs)

  def __set__(self, model_instance, value):
    if not value:
      value = unicode(os.environ['HTTP_HOST'])
    elif (value != os.environ['HTTP_HOST'] and not self.allow_read and
          not users.is_current_user_admin()):
      raise InvalidDomainError(
        "Domain '%s' attempting to illegally access data for domain '%s'"
        % (os.environ['HTTP_HOST'], value))
    super(CurrentDomainProperty, self).__set__(model_instance, value)

  def get_value_for_datastore(self, model_instance):
    value = super(CurrentDomainProperty, self).get_value_for_datastore(
      model_instance)
    if (value != os.environ['HTTP_HOST'] and
        not users.is_current_user_admin() and
        not self.allow_write):
      raise InvalidDomainError(
        "Domain '%s' attempting to allegally modify data for domain '%s'"
        % (os.environ['HTTP_HOST'], value))
    return value


class InvalidDomainError(Exception):
  """Raised when something attempts to access data belonging to another domain."""
  pass

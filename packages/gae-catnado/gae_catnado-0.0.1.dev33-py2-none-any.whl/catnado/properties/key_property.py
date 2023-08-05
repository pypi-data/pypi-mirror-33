from google.appengine.ext import db


class KeyProperty(db.Property):
  """Property that stores a key without automatically dereferencing it.

  Note that the default alternative, `db.ReferenceProperty`, performs a
  datastore RPC when it is accessed, which can lead to hidden performance
  problems.

  Furthermore, it needs to have the Kind specified when it is declared, which
  creates a code dependency between models that can be undesirable.

  `KeyProperty` helps alleviate these concerns.
  """

  def __init__(self, *args, **kwargs):
    """Constructor.

    Args:
      kind: optional string; datastore kind for validation
    """
    super(KeyProperty, self).__init__(*args, **kwargs)
    self.kind = kwargs.get('kind')

  def validate(self, value):
    """Validate value is a key or model.

    Args:
      value: The value to validate.
    Returns:
      google.appengine.ext.db.Key
    Raises:
      TypeError if the value can't be converted into a `db.Key`
    """
    if isinstance(value, basestring):
      value = db.Key(value)
    elif isinstance(value, db.Model):
      value = value.key()
    if value is not None:
      if not isinstance(value, db.Key):
        raise TypeError(
          '{} must be an instance of db.Key, got {}'.format(self.name, type(value))
        )
      if self.kind and value.kind() != self.kind:
        raise TypeError('%s must be a %s' % self.kind)
    return super(KeyProperty, self).validate(value)

from google.appengine.ext import db

from catnado.properties.key_property import KeyProperty


class UniquePropertyRecord(db.Model):
  """Helper class for unique datastore properties.

  This works by creating a Key Name using a combination of the Kind, Property
  Name, and Value. Since get_by_key_name is strongly consistent within a
  datastore transactional, we can be certain that no entity exists with a
  specific property/value.

  The type of race condition that this class is designed to prevent is a little
  difficult to write unit tests for.
  """

  target_key = KeyProperty()

  @staticmethod
  def make_key_name(kind, property_name, value):
    """Make a Key Name given a kind, property name, and value.

    Args:
      kind: required str or db.Model subclass
      property_name: required str; property name i.e. "email"
      value: required value (that can be converted to a string)

    Returns:
      str to be used as a Key Name

    Raises:
      ValueError if kind is not a string or db.Model subclass
    """
    if isinstance(kind, type) and issubclass(kind, db.Model):
      kind = kind.kind()
    if not isinstance(kind, basestring):
      raise ValueError('kind must be a string or db.Model subclass')

    return '{}:{}:{}'.format(kind, property_name, value)

  @staticmethod
  def create(kind, property_name, value, target_key=None, transactional=True,
             allow_none=False):
    """Create a UniquePropertyRecord.

    Args:
      (see make_key_name)
      target_key: optional db.Model subclass or key pointing at any entity
      transactional: optional bool, whether to create in a transaction (True)

    Returns:
      UniquePropertyRecord key, if one was created
      None otherwise

    Raises:
      AssertionError: if value is None and allow_none is False
      ValueError: if kind is not a string or db.Model subclass
    """
    assert value is not None or allow_none

    key_name = UniquePropertyRecord.make_key_name(kind, property_name, value)

    def create_transactionally():
      preexisting_record = UniquePropertyRecord.get_by_key_name(key_name)
      if preexisting_record:
        return None

      return UniquePropertyRecord(
        key_name=key_name,
        target_key=target_key,
      ).put()

    if transactional:
      return db.run_in_transaction(create_transactionally)
    else:
      return create_transactionally()

  @staticmethod
  def retrieve(kind, property_name, value):
    """Find a UniquePropertyRecord, if it exists.

    Args:
      see create

    Returns:
      bool; True iff a UniquePropertyRecord exists with the given kind, property
        name, and value
    """
    key_name = UniquePropertyRecord.make_key_name(kind, property_name, value)
    return UniquePropertyRecord.get_by_key_name(key_name)

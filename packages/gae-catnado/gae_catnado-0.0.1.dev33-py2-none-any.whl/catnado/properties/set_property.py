from google.appengine.ext import db


class SetProperty(db.ListProperty):
  """A property that stores a set of things.

  This is a parameterized property; the parameter must be a valid
  non-list data type, and all items must conform to this type.
  """
  def validate(self, value):
    value = db.Property.validate(self, value)
    if value is not None:
      if not isinstance(value, (set, frozenset)):
        raise db.BadValueError('Property %s must be a set' % self.name)

      value = self.validate_list_contents(value)
    return value

  def default_value(self):
    return set(db.Property.default_value(self))

  def get_value_for_datastore(self, model_instance):
    return list(super(SetProperty, self).get_value_for_datastore(model_instance))

  def make_value_from_datastore(self, value):
    if value is not None:
      return set(super(SetProperty, self).make_value_from_datastore(value))

  def get_form_field(self, **kwargs):
    from django import newforms as forms
    defaults = {'widget': forms.Textarea,
                'initial': ''}
    defaults.update(kwargs)
    return super(SetProperty, self).get_form_field(**defaults)

  def get_value_for_form(self, instance):
    value = super(SetProperty, self).get_value_for_form(instance)
    if not value:
      return None
    if isinstance(value, set):
      value = '\n'.join(value)
    return value

  def make_value_from_form(self, value):
    if not value:
      return []
    if isinstance(value, basestring):
      value = value.splitlines()
    return set(value)

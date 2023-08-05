from google.appengine.ext import db


class ChoiceProperty(db.IntegerProperty):
  """A property for efficiently storing choices made from a finite set.

  This works by mapping each choice to an integer.  The choices must be hashable
  (so that they can be efficiently mapped back to their corresponding index).
  """

  def __init__(self, choices, make_choice_attrs=True, *args, **kwargs):
    """Constructor.

    Args:
      choices: A non-empty list of 2-tuples of the form (id, choice). id must be
        the int to store in the database.  choice may be any hashable value.
      make_choice_attrs: If True, the uppercase version of each string choice is
        set as an attribute whose value is the choice's int representation.
    """
    super(ChoiceProperty, self).__init__(*args, **kwargs)
    self.index_to_choice = dict(choices)
    self.choice_to_index = dict((c, i) for i, c in self.index_to_choice.iteritems())
    if make_choice_attrs:
      for i, c in self.index_to_choice.iteritems():
        if isinstance(c, basestring):
          setattr(self, c.upper(), i)

  def get_choices(self):
    """Get a list of values which may be assigned to this property."""
    return self.choice_to_index.keys()

  def c2i(self, choice):
    """Convert a choice to its datastore representation."""
    return self.choice_to_index[choice]

  def __get__(self, model_instance, model_class):
    if model_instance is None:
      return self
    index = super(ChoiceProperty, self).__get__(model_instance, model_class)
    return self.index_to_choice[index]

  def __set__(self, model_instance, value):
    try:
      index = self.c2i(value)
    except KeyError:
      raise db.BadValueError('Property %s must be one of the allowed choices: %s' %
                             (self.name, self.get_choices()))
    super(ChoiceProperty, self).__set__(model_instance, index)

  def get_value_for_datastore(self, model_instance):
    """Use underlying int value for datastore."""
    return super(ChoiceProperty, self).__get__(model_instance, model_instance.__class__)

  def make_value_from_datastore(self, value):
    """Convert int from datastore to choice."""
    if value is None:
      return None
    return self.index_to_choice[value]

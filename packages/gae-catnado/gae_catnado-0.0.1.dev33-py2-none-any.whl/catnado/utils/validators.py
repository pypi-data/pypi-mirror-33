import logging


CLEAN_DATA = 'clean_data'
ERROR_EXTRA_VALIDATORS_NO_TYPE = 'one of type or extra validators is required'


class ValidationError(Exception):
  """Raise when a request validation decorator fails.

  See: validate.
  """

  pass


def validate(key, new_type, extra_validators=None, required=False):
  """Use as a decorator to validate incoming request data.

  The validated request data is stored on `self.request.clean_data` so that it
  can be used by the handler later.

  Args:
    key: the request data key to validate
    new_type: optional desired type; if None, you must specify extra_validators
      note: arg (not kwarg) because it should be specified most of the time.
      This type must be instantiable! i.e. use unicode, not basestring.
    extra_validators: optional validator func (or funcs)
    required: optional bool; whether this field is required (defaults False)

  Raises:
    AssertionError: if type_ is not a type
    ValidationError: if the value is missing and required or if the value can't
      be converted to the given type
  """
  def outer_decorator(func):
    def inner_decorator(self, *args, **kwargs):

      assert isinstance(new_type, (list, type))

      value = self.request.params.get(key)

      if value is None and required:
        logging.error('{} is required but missing'.format(key))
        self.abort(400)

      if new_type:
        try:
          new_value = new_type(value)
        # in general it's bad to do this, but this avoids an HTTP 500
        except Exception as e:
          # we make up for the badness of catching all exceptions by logging it
          logging.error('Validator caught exception {} while handling request'.format(e))
          self.abort(400, detail='{} contains invalid input'.format(key))
          return  # just to get PyCharm to stop complaining
      else:
        assert extra_validators, ERROR_EXTRA_VALIDATORS_NO_TYPE
        new_value = value

      if extra_validators:
        if not isinstance(extra_validators, list):
          validators_to_run = [extra_validators]
        else:
          assert isinstance(extra_validators, list)
          validators_to_run = extra_validators

        for extra_validator in validators_to_run:
          try:
            new_value = extra_validator(new_value)
          except ValidationError:
            logging.error('{} failed'.format(extra_validator))
            self.abort(400)

      clean_data = self.request.registry.setdefault(CLEAN_DATA, {})
      clean_data[key] = new_value

      func(self, *args, **kwargs)

    return inner_decorator
  return outer_decorator

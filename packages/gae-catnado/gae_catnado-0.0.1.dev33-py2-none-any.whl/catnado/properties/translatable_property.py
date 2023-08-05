from google.appengine.ext import db
import pycountry

from catnado.properties.pickle_property import PickleProperty


# fallback language if a translation cannot be found
FALLBACK_LANGUAGE = 'en'


def is_valid_iso639_language_code(language_code):
  """ Check a 2 letter ISO-639 language code is valid

  Args:
    language_code: 2 letter ISO-639 language code

  Returns:
    boolean indicating whether the language was found in pycountries.languages
  """
  try:
    pycountry.languages.get(alpha_2=language_code)
  except KeyError:
    return False

  return True


class MissingTranslationError(Exception):
  """ Raised when the requested language is missing
  """
  pass


class InvalidLanguageError(Exception):
  """ Raised when a requested 2-letter language code cannot be found
  """
  pass


class TranslationDictionary(dict):
  """ A dictionary with convenience functions for fetching a translation.
  """

  def get_translation(self, model_instance, language_code, allow_fallback=True):
    """ Get the translation of the string in the given language.

    Args:
      model_instance: model instance this property is attached to
      language_code: str; an ISO-639 2 letter language code
      fallback: str; fallback language code (or True for English)

    Raises:
      MissingTranslationError: if a translation could not be found
      InvalidLanguageError: if `language_code` is not a valid ISO-639 2 letter
        language code

    Returns:
      unicode string
    """
    data = self.__get__(model_instance, model_instance.__class__)

    if not is_valid_iso639_language_code(language_code):
      raise InvalidLanguageError(language_code)

    if language_code in data:
      translation = data.get(language_code)

    elif allow_fallback:
      if isinstance(allow_fallback, basestring) and allow_fallback in data:
        translation = data.get(allow_fallback)
      else:
        translation = data.get(FALLBACK_LANGUAGE)

    return translation


class TranslatableStringProperty(PickleProperty):
  """ A PickleProperty subclass intended to store translations of a string as a
  dictionary mapping two-letter language codes to Unicode translations:

  {
    'en': 'translation',
    'es': 'translation'
  }

  Validator checks each language key against ISO-639 and converts all key/value
  pairs to Unicode.
  """

  def make_value_from_datastore(self, value):
    raw_dict = super(PickleProperty, self).make_value_from_datastore(value)

  def validate(self, value):
    """
    Raises:
      db.BadValueError: if any language code is invalid or any entry is not a
        string
    """
    if not isinstance(value, dict):
      raise db.BadValueError('TranslatableStringProperty must be a dict')

    output = {}
    for k, v in value.iteritems():
      k = k.lower()

      if not (isinstance(k, basestring) and isinstance(v, basestring)):
        raise db.BadValueError('all keys/values must be strings')

      if not self._language_exists(k):
        detail = '{} is not a valid ISO-639 2 letter language code'.format(k)
        raise db.BadValueError(detail)

      output[unicode(k.lower())] = unicode(v)

    return output

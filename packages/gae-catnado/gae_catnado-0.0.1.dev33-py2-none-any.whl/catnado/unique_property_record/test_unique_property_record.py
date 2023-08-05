from google.appengine.ext import db

from catnado.testing.testcase import SimpleAppEngineTestCase
from catnado.unique_property_record import UniquePropertyRecord

NAME = 'name'
TEST = 'test'
UNIQUE_NAME = 'unique_name'
PARENT = 'parent'


class SimpleTestModel(db.Model):
  unique_name = db.StringProperty()


class UniquePropertyRecordTest(SimpleAppEngineTestCase):

  def test_duplicate_key_raises_exception(self):
    UniquePropertyRecord.create(TEST, TEST, TEST)
    self.assertIsNone(UniquePropertyRecord.create(TEST, TEST, TEST))

    UniquePropertyRecord.create(SimpleTestModel, UNIQUE_NAME, NAME)
    self.assertIsNone(UniquePropertyRecord.create(SimpleTestModel, UNIQUE_NAME, NAME))

  def test_nones_disallowed_unless_specified(self):
    with self.assertRaises(AssertionError):
      UniquePropertyRecord.create(TEST, TEST, None)
    UniquePropertyRecord.create(TEST, TEST, None, allow_none=True)

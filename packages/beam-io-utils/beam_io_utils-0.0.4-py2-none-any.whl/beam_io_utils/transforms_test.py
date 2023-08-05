import unittest

import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

from beam_io_utils.transforms import Dedupe

class TestDedupeTransform(unittest.TestCase):
  input_data = [
      {'a': 1, 'b': 2},
      {'a': 3, 'b': 4},
      {'a': 1, 'b': 2},
      {'a': 3, 'b': 4},
      {'a': 1, 'b': 2},
  ]

  def test_transform_simple(self):
    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    deduped = (collection | 'dedupe' >> Dedupe(lambda r: sum(r.values())))

    assert_that(
        deduped,
        equal_to([{'a': 1, 'b': 2},
                  {'a': 3, 'b': 4}]))

    deduped.pipeline.run()

if __name__ == '__main__':
  unittest.main()

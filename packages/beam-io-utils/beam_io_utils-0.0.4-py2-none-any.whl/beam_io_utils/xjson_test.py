import unittest

import os

import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

from beam_io_utils.xjson import JSONFileBasedSource, WriteToJSON

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "..", "example_data", "vs_aud.json")
output_dest = os.path.join(dirname, "..", "example_output", "processed")

class TestJSONSourceAndSink(unittest.TestCase):
  data = [
      {u'symbol': u'GBP', u'rate': 0.56514},
      {u'symbol': u'EUR', u'rate': 0.63581},
      {u'symbol': u'CHF', u'rate': 0.73569},
      {u'symbol': u'USD', u'rate': 0.78389},
      {u'symbol': u'CAD', u'rate': 0.98474},
      {u'symbol': u'SGD', u'rate': 1.0373},
      {u'symbol': u'NZD', u'rate': 1.078},
      {u'symbol': u'BGN', u'rate': 1.2435},
      {u'symbol': u'BRL', u'rate': 2.5675},
      {u'symbol': u'PLN', u'rate': 2.6478},
      {u'symbol': u'ILS', u'rate': 2.7321},
      {u'symbol': u'RON', u'rate': 2.953},
      {u'symbol': u'TRY', u'rate': 2.9659},
      {u'symbol': u'MYR', u'rate': 3.0689},
      {u'symbol': u'HRK', u'rate': 4.7277},
      {u'symbol': u'DKK', u'rate': 4.7323},
      {u'symbol': u'CNY', u'rate': 4.9241},
      {u'symbol': u'HKD', u'rate': 6.1294},
      {u'symbol': u'NOK', u'rate': 6.1677},
      {u'symbol': u'SEK', u'rate': 6.2745},
      {u'symbol': u'ZAR', u'rate': 9.4557},
      {u'symbol':u'MXN', u'rate': 14.746},
      {u'symbol': u'CZK', u'rate': 16.043},
      {u'symbol': u'THB', u'rate': 24.759},
      {u'symbol': u'PHP', u'rate': 40.402},
      {u'symbol': u'RUB', u'rate': 44.959},
      {u'symbol': u'INR', u'rate': 50.383},
      {u'symbol': u'ISK', u'rate': 79.476},
      {u'symbol': u'JPY', u'rate': 85.815},
      {u'symbol': u'HUF', u'rate': 197.51},
      {u'symbol': u'KRW', u'rate': 851.92},
      {u'symbol': u'IDR', u'rate': 10642}
  ]

  # TODO: This is not testing for newlines present in values... I (@axdg) need
  # to make sure that works.
  def test_reading(self):
    p = TestPipeline()
    collection = (p | "read_file" >> beam.io.Read(JSONFileBasedSource(filename)))

    assert_that(
        collection,
        equal_to(self.data))

    collection.pipeline.run()


  # TODO: All this is really testing is that nothing throws...
  def test_writing(self):
    p = TestPipeline()

    collection = (
      p | 'create' >> beam.Create(self.data)
        | 'write_file' >> WriteToJSON(output_dest))

    collection.pipeline.run()

if __name__ == "__main__":
  unittest.main()


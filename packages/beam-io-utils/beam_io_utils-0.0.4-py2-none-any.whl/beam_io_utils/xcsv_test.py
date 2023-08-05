import unittest

import os

import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

from beam_io_utils.xcsv import CSVFileBasedSource, WriteToCSV

dirname = os.path.dirname(__file__)
csv_filename = os.path.join(dirname, "..", "example_data", "vs_aud.csv")
psv_filename = os.path.join(dirname, "..", "example_data", "vs_aud.psv")
output_dest = os.path.join(dirname, "..", "example_output", "processed")

class TestCSVSourceAndSink(unittest.TestCase):
  data = [
      {"symbol": "GBP", "rate": "0.56514"},
      {"symbol": "EUR", "rate": "0.63581"},
      {"symbol": "CHF", "rate": "0.73569"},
      {"symbol": "USD", "rate": "0.78389"},
      {"symbol": "CAD", "rate": "0.98474"},
      {"symbol": "SGD", "rate": "1.0373"},
      {"symbol": "NZD", "rate": "1.078"},
      {"symbol": "BGN", "rate": "1.2435"},
      {"symbol": "IDR", "rate": "10642"},
      {"symbol": "MXN", "rate": "14.746"},
      {"symbol": "CZK", "rate": "16.043"},
      {"symbol": "HUF", "rate": "197.51"},
      {"symbol": "BRL", "rate": "2.5675"},
      {"symbol": "PLN", "rate": "2.6478"},
      {"symbol": "ILS", "rate": "2.7321"},
      {"symbol": "RON", "rate": "2.953"},
      {"symbol": "TRY", "rate": "2.9659"},
      {"symbol": "THB", "rate": "24.759"},
      {"symbol": "MYR", "rate": "3.0689"},
      {"symbol": "HRK", "rate": "4.7277"},
      {"symbol": "DKK", "rate": "4.7323"},
      {"symbol": "CNY", "rate": "4.9241"},
      {"symbol": "PHP", "rate": "40.402"},
      {"symbol": "RUB", "rate": "44.959"},
      {"symbol": "INR", "rate": "50.383"},
      {"symbol": "HKD", "rate": "6.1294"},
      {"symbol": "NOK", "rate": "6.1677"},
      {"symbol": "SEK", "rate": "6.2745"},
      {"symbol": "ISK", "rate": "79.476"},
      {"symbol": "JPY", "rate": "85.815"},
      {"symbol": "KRW", "rate": "851.92"},
      {"symbol": "ZAR", "rate": "9.4557"}
  ]

  fieldnames = ['symbol', 'rate']

  def test_reading_csv(self):
    p = TestPipeline()
    collection = (p | "read_file" >> beam.io.Read(CSVFileBasedSource(csv_filename)))

    assert_that(
        collection,
        equal_to(self.data))

    collection.pipeline.run()

  def test_reading_psv(self):
    p = TestPipeline()
    collection = (p | "read_file" >> beam.io.Read(CSVFileBasedSource(psv_filename, delimiter='|')))

    assert_that(
        collection,
        equal_to(self.data))

    collection.pipeline.run()

  def test_writing(self):
    # TODO: All this is really testing is that nothing throws...
    p = TestPipeline()

    collection = (
      p | 'create' >> beam.Create(self.data)
        | 'write_file' >> WriteToCSV(
              self.fieldnames,
              output_dest))

    collection.pipeline.run()

if __name__ == "__main__":
  unittest.main()


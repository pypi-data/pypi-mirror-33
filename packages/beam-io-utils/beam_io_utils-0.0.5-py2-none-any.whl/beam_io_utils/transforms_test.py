import unittest

import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

from beam_io_utils.transforms import Tuple
from beam_io_utils.transforms import Dedupe
from beam_io_utils.transforms import Group
from beam_io_utils.transforms import GroupReduce
from beam_io_utils.transforms import Enrich
from beam_io_utils.transforms import MergeOneLeft

class TestTuple(unittest.TestCase):
  input_data = [
      {'a': 1, 'b': ['x', 'y', 'z']},
      {'a': 3, 'b': ['x']},
      {'a': 1, 'b': ['x', 'z']},
      {'a': 3, 'b': ['x', 'y', 'z']},
      {'a': 1, 'b': ['y', 'z']},
  ]

  # NOTE: A simple, 2-tupling using a key.
  def test_tuple_key(self):
    key = 'a'

    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    tuples = (collection | 'tuple' >> Tuple(key))

    assert_that(
        tuples,
        equal_to([
              (1, {'a': 1, 'b': ['x', 'y', 'z']}),
              (1, {'a': 1, 'b': ['x', 'z']}),
              (1, {'a': 1, 'b': ['y', 'z']}),
              (3, {'a': 3, 'b': ['x']}),
              (3, {'a': 3, 'b': ['x', 'y', 'z']})]))

    tuples.pipeline.run()


  # NOTE: Using a function, grab the first value in a nested array.
  def test_tuple_func(self):

    def key_func(record):
      return record['b'][0]

    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    tuples = (collection | 'tuple' >> Tuple(key_func))

    assert_that(
        tuples,
        equal_to([
            ('x', {'a': 1, 'b': ['x', 'y', 'z']}),
            ('x', {'a': 1, 'b': ['x', 'z']}),
            ('x', {'a': 3, 'b': ['x']}),
            ('x', {'a': 3, 'b': ['x', 'y', 'z']}),
            ('y', {'a': 1, 'b': ['y', 'z']})]))

    tuples.pipeline.run()


  # NOTE: Using a function returning an array to make many 2-Tuples per input
  # element. This would be quite useful where we want to group elements based
  # on nested values.
  def test_tuple_func_array(self):

    def key_gen(record):
      # NOTE: This is any array, we get one value for each item in it.
      return record.get('b')

    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    expanded = (collection | 'tuple' >> Tuple(key_gen))

    assert_that(
        expanded,
        equal_to([
          ('x', {'a': 1, 'b': ['x', 'y', 'z']}),
          ('x', {'a': 1, 'b': ['x', 'z']}),
          ('x', {'a': 3, 'b': ['x']}),
          ('x', {'a': 3, 'b': ['x', 'y', 'z']}),
          ('y', {'a': 1, 'b': ['x', 'y', 'z']}),
          ('y', {'a': 1, 'b': ['y', 'z']}),
          ('y', {'a': 3, 'b': ['x', 'y', 'z']}),
          ('z', {'a': 1, 'b': ['x', 'y', 'z']}),
          ('z', {'a': 1, 'b': ['x', 'z']}),
          ('z', {'a': 1, 'b': ['y', 'z']}),
          ('z', {'a': 3, 'b': ['x', 'y', 'z']})]))

    expanded.pipeline.run()


class TestDedupe(unittest.TestCase):
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


class TestGroup(unittest.TestCase):
  input_data = [
      {'a': 'x', 'b': 1},
      {'a': 'x', 'b': 2},
      {'a': 'x', 'b': 3},
      {'a': 'x', 'b': 4},
      {'a': 'x', 'b': 5},
      {'a': 'y', 'b': 1},
      {'a': 'y', 'b': 1},
      {'a': 'y', 'b': 1},
      {'a': 'z', 'b': 2},
      {'a': 'z', 'b': 3},
  ]


  def test_transform_function(self):
    key = 'a'

    # Passing a function.
    def group_func(records):
      return [{'name': records[0]['a'], 'count': len(records)}]

    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    grouped = (collection | 'group' >> Group(key, group_func))

    assert_that(
        grouped,
        equal_to([
            {'count': 2, 'name': 'z'},
            {'count': 3, 'name': 'y'},
            {'count': 5, 'name': 'x'}]))

    grouped.pipeline.run()


  def test_transform_generator(self):
    key = 'a'

    # Passing a generator function.
    # NOTE: This is identical to above, but it uses a generator function in place
    # of a regular function.
    def group_gen(records):
      yield {'name': records[0]['a'], 'count': len(records)}

    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    grouped = (collection | 'group' >> Group(key, group_gen))

    assert_that(
        grouped,
        equal_to([
            {'count': 2, 'name': 'z'},
            {'count': 3, 'name': 'y'},
            {'count': 5, 'name': 'x'}]))

    grouped.pipeline.run()


  def test_transform_partition(self):
    key = 'a'

    # Passing a generator function.
    # NOTE: This example replicates the behaviour of a `PARTITION OVER` SQL query.
    def group_gen(records):
      count = len(records)
      total = sum([v['b'] for v in records])

      for r in records: # pylint: disable=invalid-name
        record = dict()
        record.update(r)
        record.update({'count': count, 'total': total})
        yield record

    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    partitioned = (collection | 'group' >> Group(key, group_gen))

    assert_that(
        partitioned,
        equal_to([
            {'a': 'x', 'count': 5, 'b': 1, 'total': 15},
            {'a': 'x', 'count': 5, 'b': 2, 'total': 15},
            {'a': 'x', 'count': 5, 'b': 3, 'total': 15},
            {'a': 'x', 'count': 5, 'b': 4, 'total': 15},
            {'a': 'x', 'count': 5, 'b': 5, 'total': 15},
            {'a': 'y', 'count': 3, 'b': 1, 'total': 3},
            {'a': 'y', 'count': 3, 'b': 1, 'total': 3},
            {'a': 'y', 'count': 3, 'b': 1, 'total': 3},
            {'a': 'z', 'count': 2, 'b': 2, 'total': 5},
            {'a': 'z', 'count': 2, 'b': 3, 'total': 5}]))

    partitioned.pipeline.run()


class TestGroupReduce(unittest.TestCase):
  input_data = [
      {'a': 'x', 'b': 1},
      {'a': 'x', 'b': 2},
      {'a': 'x', 'b': 3},
      {'a': 'x', 'b': 4},
      {'a': 'x', 'b': 5},
      {'a': 'y', 'b': 1},
      {'a': 'y', 'b': 1},
      {'a': 'y', 'b': 1},
      {'a': 'z', 'b': 2},
      {'a': 'z', 'b': 3},
  ]


  def test_transform(self):
    # NOTE: This function should return the key for joining.
    def key_func(value):
      return value['a']


    # NOTE: This function gets passed all the grouped elements as an array.
    def reducer_func(previous, current):
      previous['a'] = current['a']
      if previous.get('b', None) is None:
        previous['b'] = list()
      previous['b'].append(current['b'])
      previous['c'] = sum(previous['b'])
      return previous


    # NOTE: This just needs to return the initial value for reduction.
    def initializer_func():
      return dict()

    pipeline = TestPipeline()
    collection = (pipeline | 'create' >> beam.Create(self.input_data))
    grouped = (collection | 'group' >> GroupReduce(key_func, reducer_func, initializer_func))

    assert_that(
        grouped,
        equal_to([
            {'a': 'x', 'c': 15, 'b': [1, 2, 3, 4, 5]},
            {'a': 'y', 'c': 3, 'b': [1, 1, 1]},
            {'a': 'z', 'c': 5, 'b': [2, 3]}]))

    grouped.pipeline.run()

    return


class TestEnrich(unittest.TestCase):
  simple_input_records = [
      {'a': 'x', 'b': 3},
      {'a': 'y', 'b': 1},
      {'a': 'z', 'b': 2},
  ]

  simple_input_partners = [
      {'a': 'x', 'c': 1},
      {'a': 'y', 'c': 4},
      {'a': 'z', 'c': 2},
  ]

  # NOTE: This is equivalent to `MergeOneLeft`
  def test_transform(self):
    def key(value):
      # NOTE: This is equivalent to simply passing `a` as a key string.
      return value['a']

    def merge(records, partners):
      d = dict() # pylint: disable=invalid-name
      record = records[0]
      partner = partners[0]
      d.update(record)
      d.update(partner)

      yield d

    pipeline = TestPipeline()
    records = (pipeline | 'create_records' >> beam.Create(self.simple_input_records))
    partners = (pipeline | 'create_partners' >> beam.Create(self.simple_input_partners))

    grouped = records | 'merge' >> Enrich(key, partners, merge)

    assert_that(
        grouped,
        equal_to([
            {'a': 'z', 'c': 2, 'b': 2},
            {'a': 'y', 'c': 4, 'b': 1},
            {'a': 'x', 'c': 1, 'b': 3}]))

    grouped.pipeline.run()

class TestMergeOneLeft(unittest.TestCase):
  simple_input_records = [
      {'a': 'x', 'b': 3},
      {'a': 'y', 'b': 1},
      {'a': 'z', 'b': 2},
  ]

  simple_input_partners = [
      {'a': 'x', 'c': 1},
      {'a': 'y', 'c': 4},
      {'a': 'z', 'c': 2},
  ]

  # NOTE: This is equivalent to `MergeOneLeft`
  def test_transform(self):
    key = 'a'

    pipeline = TestPipeline()
    records = (pipeline | 'create_records' >> beam.Create(self.simple_input_records))
    partners = (pipeline | 'create_partners' >> beam.Create(self.simple_input_partners))

    merged = records | 'simple_left_join' >> MergeOneLeft(key, partners)

    assert_that(
        merged,
        equal_to([
            {'a': 'z', 'c': 2, 'b': 2},
            {'a': 'y', 'c': 4, 'b': 1},
            {'a': 'x', 'c': 1, 'b': 3}]))

    merged.pipeline.run()

if __name__ == '__main__':
  unittest.main()

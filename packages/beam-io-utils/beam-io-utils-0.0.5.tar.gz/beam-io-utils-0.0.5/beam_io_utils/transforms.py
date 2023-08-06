import types
import apache_beam as beam


# Performs one transform... then passes the collection through to another.
class Reemitter(beam.PTransform): # pylint: disable=no-member,too-few-public-methods

  def __init__(self, transform):
    super(Reemitter, self).__init__()
    self.transform = transform

  def expand(self, collection): # pylint: disable=arguments-differ
    (collection | self.transform) # pylint: disable=pointless-statement
    return collection


def create_tupler(key):
  """Same as `create_keyed_tuple`, but returns a function that takes the
  record to be converted."""
  if isinstance(key, basestring):
    def create_tuple(record):
      return [(record.get(key), record)]

  if callable(key):
    def create_tuple(record): # pylint: disable=function-redefined
      keys = key(record)
      if isinstance(keys, basestring):
        return [(keys, record)]

      if isinstance(keys, float) or isinstance(keys, int):
        return [(keys, record)]

      if isinstance(keys, list):
        return [(k, record) for k in keys]

  return create_tuple


class Tuple(beam.PTransform):
  """Performs a `key` tupling as a mechanism to allow `CoGroupByKey`. Used
  inside `Merge`."""

  def __init__(self, key):
    super(Tuple, self).__init__()
    self.create_tuple = create_tupler(key)

  def expand(self, collection): # pylint: disable=arguments-differ
    return (collection | beam.FlatMap(self.create_tuple)) # pylint: disable=superfluous-parens


class Untuple(beam.PTransform):
  def __init__(self):
    super(Untuple, self).__init__()

  def expand(self, collection): # pylint: disable=arguments-differ
    return (collection | beam.Map(lambda record: record[1])) # pylint: disable=superfluous-parens


# NOTE: Turns out the beam itself actually has a transform for deduplication
# built in, however it only works with string keys.
# SEE: `https`://beam.apache.org/documentation/sdks/pydoc/2.4.0/apache_beam.transforms.util.html`.
# The transform is valled `RemoveDuplicates`.
class Dedupe(beam.PTransform):
  """Given a key creator function, or a dict key name, this will create a
  dedupe transform... it's exposed as a `Ptransform so that it can act as a single
  step in a larger pipeline.`"""
  def __init__(self, key):
    super(Dedupe, self).__init__()
    self.key = key

  def expand(self, collection): # pylint: disable=arguments-differ
    return (
        collection
        | Tuple(self.key)
        | beam.GroupByKey()
        | Untuple()
        | beam.Map(lambda record: record[0])
    )


def create_reducer(reducer_fn, initilizer_fn):
  def reducer(record):
    initial = initilizer_fn()
    return reduce(reducer_fn, record, initial)

  return reducer


class Group(beam.PTransform):
  def __init__(self, group_key, group_func):
    super(Group, self).__init__()
    self.group_key = group_key

    if (isinstance(group_func, types.GeneratorType)):
      gen = group_func

      def group_func(records):
        return list(gen(records))

    self.group_func = group_func

  def expand(self, collection):
    return (
      collection
      | Tuple(self.group_key)
      | beam.GroupByKey()
      | Untuple()
      | beam.FlatMap(self.group_func)
    )


class GroupReduce(Group):
  """Performs a group by key, and then a reduce on the array of values that are
  returned... this is intended for a situation where you want to group in a dataset
  into a single value"""
  def __init__(self, group_key, rfunc=lambda p: p, ifunc=None):

    def group_func(records):
      return [reduce(rfunc, records, ifunc())]

    super(GroupReduce, self).__init__(group_key, group_func)


def create_merger(merge):
  def merger(record):
    record = record[1]

    erecords = record['record']
    epartners = record['partner']

    # Maybe use `return iter(merge(records, partners))`,
    # OR `yeild from merge(records, partners)` (python 3.3).
    for r in merge(erecords, epartners): # pylint: disable=invalid-name
      yield r

  return merger


# TODO: Rename this to `LeftJoin` - the semantics are roughly the same.
class Enrich(beam.PTransform):
  def __init__(self, key, partner, merge, partner_key=None,):
    super(Enrich, self).__init__()
    self.key = key
    self.merger = create_merger(merge)
    self.partner = partner
    self.partner_key = key if (partner_key is None) else partner_key

  def expand(self, collection): # pylint: disable=arguments-differ

    trecord = collection | 'tuple_record' >> Tuple(self.key)
    tpartner = self.partner | 'tuple_partner' >> Tuple(self.partner_key)

    return (
        {
            'record': trecord,
            'partner': tpartner
        } | 'join' >> beam.CoGroupByKey() | 'merge' >> beam.FlatMap(self.merger))


def extract_update(records, partners):
  partner = partners[0] if (len(partners) > 0) else {} # pylint: disable=len-as-condition

  for record in records:
    updated = dict()
    updated.update(record)
    updated.update(partner)
    yield updated


class MergeOneLeft(Enrich):
  """A `PTransform` that performs a specificialised merge (or left join)...
  the left collection is assumed to have a many to one relationship with the
  right collection. Pairing / Grouping is performed on the provided `key`...
  should the partner contain a different key for the join value you can pass
  the kwarg `partner_key`. This is a just a common and less generalised version
  of `Enrich`."""
  def __init__(self, key, partner, partner_key=None):
    super(MergeOneLeft, self).__init__(key, partner, extract_update, partner_key=partner_key)

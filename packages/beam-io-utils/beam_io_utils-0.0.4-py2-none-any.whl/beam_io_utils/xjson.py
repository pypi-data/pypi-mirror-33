import json

from apache_beam import PTransform
from apache_beam.coders.coders import StrUtf8Coder
from apache_beam.io import filesystem, filebasedsource, filebasedsink, Write

class FileHandleToJSONDictReader(object):

  def __init__(self, file_handle):
    self.file_handle = file_handle

  def __iter__(self):
    return self

  def next(self):
    line = self.file_handle.readline()
    if line == None or line == "":
      raise StopIteration
    return json.loads(line)


# SEE: `https://beam.apache.org/documentation/sdks/pydoc/2.2.0/apache_beam.io.filebasedsource.html#module-apache_beam.io.filebasedsource`
class JSONFileBasedSource(filebasedsource.FileBasedSource):

  def __init__(self,
               file_pattern,
               min_bundle_size=0,
               compression_type=filesystem.CompressionTypes.AUTO,
               splittable=True,
               validate=True):

    super(self.__class__, self).__init__(
        file_pattern,
        min_bundle_size=0,
        compression_type=filesystem.CompressionTypes.AUTO,
        splittable=True,
        validate=True)

  def read_records(self, file_name, offset_range_tracker):
    file_handle = self.open_file(file_name)
    iterator = FileHandleToJSONDictReader(file_handle)
    return iterator


# SEE: `https://docs.python.org/2/library/json.html`
# For serialization of JSON Lines.
class JSONFileSink(filebasedsink.FileBasedSink):
  """A little lower level."""

  def __init__(self,
               file_path_prefix,
               file_name_suffix=".json",
               num_shards=1,
               shard_name_template=None,
               coder=StrUtf8Coder(),
               compression_type=filesystem.CompressionTypes.AUTO,
               indent=None,
               separators=None,
               sort_keys=True):

    super(self.__class__, self).__init__(
        file_path_prefix=file_path_prefix,
        file_name_suffix=file_name_suffix,
        num_shards=num_shards,
        shard_name_template=shard_name_template,
        coder=coder,
        compression_type=compression_type)

    self.cache = dict()
    self.indent = indent,
    self.separators = separators,
    self.sort_keys = sort_keys,

  def open(self, temp_path):
    file_handle = super(self.__class__, self).open(temp_path)
    return file_handle

  def write_record(self, file_handle, element):
    if self.cache.get(file_handle, None) is not None:
      value = json.dumps(self.cache[file_handle])
      file_handle.write(self.coder.encode(value))
      file_handle.write("\n")

    self.cache[file_handle] = element

  def close(self, file_handle):
    if file_handle is not None:
      value = json.dumps(self.cache[file_handle])
      file_handle.write(self.coder.encode(value))

      # Write a newline at the end of the file.
      file_handle.write("\n")

    file_handle.close()


class WriteToJSON(PTransform):
  """This is the higher level `beam.PTransform` the developer should use."""

  def __init__(self,
               file_path_prefix,
               file_name_suffix=".json",
               num_shards=1,
               shard_name_template=None,
               coder=StrUtf8Coder(),
               compression_type=filesystem.CompressionTypes.AUTO,
               indent=None,
               separators=None,
               sort_keys=True):

    self.sink = JSONFileSink(
        file_path_prefix,
        file_name_suffix=".json",
        num_shards=1,
        shard_name_template=None,
        coder=StrUtf8Coder(),
        compression_type=filesystem.CompressionTypes.AUTO,
        indent=indent,
        separators=separators,
        sort_keys=sort_keys)

  def expand(self, collection):
    return collection | Write(self.sink)

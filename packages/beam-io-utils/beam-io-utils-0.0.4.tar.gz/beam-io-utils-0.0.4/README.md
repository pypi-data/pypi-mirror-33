# beam-io-utils

> Utilities for Apache Beam disk io (local or on GCP) 

[![CircleCI](https://circleci.com/gh/raywhite/beam-io-utils.svg?style=shield&circle-token=f4694e83d6aaa04718887834067be087d378dad7)](https://circleci.com/gh/raywhite/beam-io-utils)

## About

For some reason, the [Apache Beam](https://beam.apache.org/) API doesn't include flexible sources and sinks for CSV and JSON... so this module exposes those, together with some other utilities.

## Installation

Since we're keeping this module private for the time being... it can be installed using git, as follows; `pip install git+https://github.com/raywhite/beam-io-utils.git`

If developing the project, it can be cloned with `git clone https://github.com/raywhite/beam-io-utils.git`. Make sure that your environment has the necessary requirements by running;
- `pip install -r ./requirements.txt` (deps).
- `pip install -r ./requirements-dev.txt` (dev deps).

The module conforms to the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. To lint the code run `pep8 ./` from within the project root, or alternatively... you can just format the code automatically using [yapf](https://github.com/google/yapf#usage) - `yapf ./ --recursive --in-place --style pep8` (project root).

## Running Examples

The repo contains some example data (CSVs and JSON for AUD conversion rates on an arbitrary day)... you can run the subsequent exampple pipeline using `python example_pipeline.py --input example_data/vs_aud.csv --output example_output/csv_processed` for `.csv` => `.csv` or `python example_pipeline.py --input example_data/vs_aud.csv --output example_output/csv_processed --output-format=json` for `.csv` => `.json`. In both cases, the pipeline does nothing but serialize / deserialize, and dumps the output in `./example_data`.

**Code**

```python
import argparse
import logging

from beam_io_utils.csv import CSVFileBasedSource, WriteToCSV
from beam_io_utils.json import WriteToJSON
from beam_io_utils.reemitter import Reemitter

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

# TODO: This example needs a refactoring.

def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', dest='input', help='the input file(s)')
    parser.add_argument('--output', dest='output', help='the output file')
    parser.add_argument(
        '--output-format', dest='output_format', help='the output format')

    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_args.extend([
        '--runner=DirectRunner',
        '--project=SET_YOUR_PROJECT_ID_HERE',
        '--staging_location=gs://YOUR_BUCKET_NAME/AND_STAGING_DIRECTORY',
        '--temp_location=gs://YOUR_BUCKET_NAME/AND_TEMP_DIRECTORY',
        '--job_name=some_test_job',
    ])

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    with beam.Pipeline(options=pipeline_options) as p:

        if known_args.output_format == "json":
            return (p | "read_csv" >> beam.io.Read(
                CSVFileBasedSource(known_args.input))
                    | "write_json" >> WriteToJSON(known_args.output))

        fieldnames = ['symbol', 'rate']

        if known_args.output_format == "csv+json":
            return (p | "read_csv" >> beam.io.Read(
                CSVFileBasedSource(known_args.input))
                    | "write_through_csv" >> Reemitter(
                        WriteToCSV(fieldnames, known_args.output))
                    | "write_json" >> WriteToJSON(known_args.output))

        return (
            p
            | "read_csv" >> beam.io.Read(CSVFileBasedSource(known_args.input))
            | "write_csv" >> WriteToCSV(fieldnames, known_args.output))


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
```

## API

##### **csv**

csv readers and writers are proxy wrappers around the python standard [csv](https://docs.python.org/2/library/csv.html#) module, with a few minor deviations. To avoid the verbosity of passing individual formatting parameters, only [`Dialect`s](https://docs.python.org/2/library/csv.html#) for specifying delims, line terminators etc. and this always defaults to`"excel"`. To register a fancy `Dialect`s, you can do something like this;

```python
import csv
csv.register_dialect("excel-psv", delimiter="|")
```

This `Dialect` would read pipe (`|`) seperated values and could be used like this;

```python
(beam.Pipeline() 
    | "read_psv" >> CSVFileBasedSource(file_pattern, dialect="excel-psv")
    | "write_psv" >> WriteToCSV(fieldnames, file_path_prefix, dialect="excel-psv"))
```

You can also consult `./example_pipeline_custom.py` to see reading and writing with custom `Dialect`s in action.

**csv.CSVFileBasedSource(file_pattern, min_bundle_size=0, compression_type="auto", splittable=True, validate=True, fieldnames=None, restkey=None, restval=None, dialect='excel')** 

All args are standard to, and are passed through to, the underlying [`FileBasedSource`](https://beam.apache.org/documentation/sdks/pydoc/2.2.0/apache_beam.io.filebasedsource.html#apache_beam.io.filebasedsource.FileBasedSource) and [`DictReader`](https://docs.python.org/2/library/csv.html#csv.DictReader) instances. Headers can be inferred (so there is no need to provide them unless the source files do not contain headers).

**csv.WriteToCSV(fieldnames, file_path_prefix, file_name_suffix=".csv", num_shards=1, shard_name_template=None, coder=StrUtf8Coder(), compression_type="auto", restval="", extrasaction="raise", dialect="excel", include_header=True)**

The `fieldnames` and `file_path_prefix` args are required (although the fieldnames can be inferred, their intended order cannot). The `include_headers` keyword arg can be used to write files without headers. All other args are standard to, and are passed through to, the underlying [`FileBasedSink`](https://beam.apache.org/documentation/sdks/pydoc/2.2.0/apache_beam.io.filebasedsink.html#apache_beam.io.filebasedsink.FileBasedSink) and [`DictWriter`](https://docs.python.org/2/library/csv.html#csv.DictWriter) instances.

**json**

Like csv readers and writers, these are proxies to the standard [json](https://docs.python.org/2/library/json.html#module-json) module, using that modules parse and serialize functionality. All inputs / outputs are treated as arrays of json objects.

**json.JSONFileBasedSource(\*args, \*\*kwargs)** - _not implemented_

**json.WriteToJSON(file_path_prefix, file_name_suffix=".json", num_shards=1, shard_name_template=None, coder=StrUtf8Coder(), compression_type=filesystem.CompressionTypes.AUTO, indent=None, separators=None, sort_keys=True)**

The `file_path_prefix` args is required, keys are sorted by default. The `lines` key word are can be set to `True` in order to write to the JSON lines format (single minfied object per line, file is flanked with array opening / closing brackets)... and this will overwrite all other formatting parameters. All other args are standard to, and are passed through to, the underlying [`FileBasedSink`](https://beam.apache.org/documentation/sdks/pydoc/2.2.0/apache_beam.io.filebasedsink.html#apache_beam.io.filebasedsink.FileBasedSink) instance [`json.dumps`](https://docs.python.org/2/library/json.html#json.dumps) invocation.

##### **transforms**

**transforms.Reemitter(transform)**

This will just wrap any transform instance that behaves as a `Sink`, so that it both writes to whatever destination and then re emits the input `PCollection`... and axample of it's usage would be;

```python
(beam.Pipeline() | "read_csv" >> beam.io.Read(CSVFileBasedSource(file_pattern))
                 | "write_through_csv" >> Reemitter(WriteToCSV(fieldnames, file_path_prefix))
                 | "write_json" >> WriteToJSON(file_path_prefix))
```

**transforms.Dedupe(key_fn)**

This is another composite transform for depuplication of `Pvalue`s (it actually performs a `GroupByKey` on tupled values under the hood). The test case documents the usage pretty well, but essentilly the passed `key_fn` is a must be a function that accepts and individual value from the `PCollection` and returns a key that will be used for grouping and deduplication. For simpler use cases, a single key string (the name of some key in a `Dict`) may be used to deduplicate on the corresponding value.

## Testing / Distribution

The python environment is best set up using a virtual environment for handling pinning of dependancies, and the correct python version (`v2.7`). In order to create the correct virtual environment, you can do something like this (on mac, see the circle configuration for linux instructions);

```sh
$ virtualenv --python /usr/bin/python2.7 ./venv
$ chmod +x ./venv/bin/activate
$ . ./venv/bin/activate
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
$ echo "do some stuff... like run tests"
```

To test the code you can use `python -m unittest discover ./beam_io_utils "*test.py"`.

**NOTE:** Tests are a WIP.

Each test file is named for the corresponding file being tested, and is located in the same directory (`beam_io_utils`). To run all python tests use; `python -m unittest discover ./src "*test.py"`.

Lint can be checked using [pylint](https://www.pylint.org/); `pylint -r n ./beam_io_utils ./setup.py`.

You can distribute the package by following the instructions at [this page on python.org](https://packaging.python.org/tutorials/packaging-projects/);

```sh
# NOTE: Make sure you're inside an activated virtualenv;
python -m pip install --upgrade setuptools wheel
python -m pip install --upgrade twine

# Build the tarballs.
python setup.py sdist bdist_wheel

# Upload / publish a new version.
twine upload dist/*
```

## License

&bull; **MIT** &copy; Ray White, 2017-2018 &bull;

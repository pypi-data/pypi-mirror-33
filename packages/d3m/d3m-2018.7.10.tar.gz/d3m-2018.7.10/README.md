# Common code for D3M project

This package provides a core package for D3M project with common code available.
It contains standard interfaces, reference implementations, and utility implementations.

## About Data Driven Discovery Program

DARPA Data Driven Discovery (D3M) Program is researching ways to get machines to build
machine learning pipelines automatically. It is split into three layers:
TA1 (primitives), TA2 (systems which combine primitives automatically into pipelines
and executes them), and TA3 (end-users interfaces).

## Installation

This package works with Python 3.6+. You need to have the following packages installed on the system (for Debian/Ubuntu):

* `libssl-dev`
* `libcurl4-openssl-dev`

You can install latest stable version from [PyPI](https://pypi.org/):

```
$ pip3 install --process-dependency-links d3m
```

If you also want support for [Arrow](https://arrow.apache.org/), use:

```
$ pip3 install --process-dependency-links d3m[arrow]
```

To install latest development version:

```
$ pip3 install --process-dependency-links git+https://gitlab.com/datadrivendiscovery/d3m.git@devel
```

`--process-dependency-links` argument is required for correct processing of dependencies.

When cloning a repository, clone it recursively to get also git submodules:

```
$ git clone --recursive https://gitlab.com/datadrivendiscovery/d3m.git
```

## Changelog

See [HISTORY.md](./HISTORY.md) for summary of changes to this package.

## Repository structure

`master` branch contains latest stable release of the package.
`devel` branch is a staging branch for the next release.

Releases are [tagged](https://gitlab.com/datadrivendiscovery/d3m/tags).

# Python namespace for D3M project

## Primitives D3M namespace

The `d3m.primitives` module exposes all primitives under the same `d3m.primitives` namespace.

This is achieved using [Python entry points](https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins).
Python packages containing primitives should register them and expose them under the common
namespace by adding an entry like the following to package's `setup.py`:

```python
entry_points = {
    'd3m.primitives': [
        'primitive_namespace.PrimitiveName = my_package.my_module:PrimitiveClassName',
    ],
},
```

The example above would expose the `my_package.my_module.PrimitiveClassName` primitive under
`d3m.primitives.primitive_namespace.PrimitiveName`.

Configuring `entry_points` in your `setup.py` does not just put primitives into a common namespace, but also
helps with discovery of your primitives on the system. Then your package with primitives just have to be
installed on the system and can be automatically discovered and used by any other Python code.

>**Note:**
Only primitive classes are available thorough  the `d3m.primitives` namespace, not other symbols
from a source module. In the example above, only `PrimitiveClassName` is available, not other
symbols inside `my_module` (except if they are other classes also added to entry points).

<!-- -->
>**Note:**
Modules under `d3m.primitives` are created dynamically at run-time based on information from
entry points. So some tools (IDEs, code inspectors, etc.) might not find them because there are
no corresponding files and directories under `d3m.primitives` module. You have to execute Python
code for modules to be available. Static analysis cannot find them.

## Primitives discovery on PyPi

To facilitate automatic discovery of primitives on PyPi (or any other compatible Python Package Index),
publish a package with a keyword `d3m_primitive` in its `setup.py` configuration:

```python
keywords='d3m_primitive'
```

>**Note:**
Be careful when automatically discovering, installing, and using primitives from unknown sources.
While primitives are designed to be bootstrapable and automatically installable without human
involvement, there are no isolation mechanisms yet in place for running potentially malicious
primitives. Currently recommended way is to use manually curated lists of known primitives.

## Python functions available

The `d3m.index` module exposes the following Python utility functions.

### `d3m.index.search`

Returns a list of primitive paths (Python paths under `d3m.primitives` namespace)
for all known (discoverable through entry points) primitives, or limited by the
`primitive_path_prefix` search argument.

### `d3m.get_primitive`

Loads (if not already) a primitive class and returns it.

### `get_primitive_by_id`

Returns a primitive class based on its ID from all currently loaded primitives.

### `get_loaded_primitives`

Returns a list of all currently loaded primitives.

### `load_all`

Loads all primitives available and populates `d3m.primitives` namespace with them.

### `d3m.index.register_primitive`

Registers a primitive under `d3m.primitives` namespace.

This is useful to register primitives not necessary installed on the system
or which are generated at runtime. It is also useful for testing purposes.

### `d3m.index.discover`

Returns package names from PyPi which provide D3M primitives.

This is determined by them having a `d3m_primitive` among package keywords.

## Command line

The `d3m.index` module also provides a command line interface by running
`python -m d3m.index`. The following commands are currently available.

Use `-h` or `--help` argument to obtain more information about each command
and its arguments.

### `python -m d3m.index search`

Searches locally available primitives. Lists registered Python paths
for primitives installed on the system.

### `python -m d3m.index discover`

Discovers primitives available on PyPi. Lists package names containing D3M
primitives on PyPi.

### `python -m d3m.index describe`

Generates a JSON description of a primitive.

# Metadata for values and primitives

Metadata is a core component of any data-based system.
This repository is standardizing how we represent metadata in the D3M program
and focusing on three types of metadata:
* metadata associated with primitives
* metadata associated with datasets
* metadata associated with values passed inside pipelines

This repository is also standardizing types of values being passed between
primitives in pipelines.
While theoretically any value could be passed between primitives, limiting
them to a known set of values can make primitives more compatible,
efficient, and values easier to introspect by TA3 systems.

## Container types

All input and output (container) values passed between primitives should expose a `Sequence`
[protocol](https://www.python.org/dev/peps/pep-0544/) (sequence in samples) and
provide `metadata` attribute with metadata.

`d3m.container` module exposes such standard types:

* `Dataset` – a class representing datasets, including D3M datasets, implemented in [`d3m.container.dataset`](d3m/container/dataset.py) module
* `DataFrame` – [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html) with support for `metadata` attribute,
  implemented in [`d3m.container.pandas`](d3m/container/pandas.py) module
* `ndarray` – [`numpy.ndarray`](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html) with support for `metadata` attribute,
  implemented in [`d3m.container.numpy`](d3m/container/numpy.py) module
* `matrix` – [`numpy.matrix`](https://docs.scipy.org/doc/numpy/reference/generated/numpy.matrix.html) with support for `metadata` attribute,
  implemented in [`d3m.container.numpy`](d3m/container/numpy.py) module
* `List` – a standard `list` with support for `metadata` attribute, implemented in [`d3m.container.list`](d3m/container/list.py) module

`List` can be used to create a simple list container.

It is strongly encouraged to use the `DataFrame` container type for primitives which do not have strong
reasons to use something else (`Dataset`s to operate on inital pipeline input, or optimized high-dimensional packed data in `ndarray`s,
or lists to pass as values to hyper-parameters). This makes it easier to operate just on columns without type casting while the data
is being transformed to make it useful for models.

When deciding which container type to use for inputs and outputs of a primitive, consider as well where an expected place
for your primitive is in the pipeline. Generally, pipelines tend to have primitives operating on `Dataset` at the
beginning, then use `DataFrame` and then convert to `ndarray`.

## Data types

Container types can contain values of the following types:
* container types themselves
* Python builtin primitive types:
  * `str`
  * `bytes`
  * `bool`
  * `float`
  * `int`
  * `dict` (consider using [`typing.Dict`](https://docs.python.org/3/library/typing.html#typing.Dict),
    [`typing.NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple),
    or [`TypedDict`](https://mypy.readthedocs.io/en/stable/kinds_of_types.html#typeddict))
  * `NoneType`
* NetworkX [`Graph`](https://networkx.github.io/documentation/stable/reference/classes/graph.html),
  [`DiGraph`](https://networkx.github.io/documentation/stable/reference/classes/digraph.html),
  [`MultiGraph`](https://networkx.github.io/documentation/stable/reference/classes/multigraph.html),
  [`MultiDiGraph`](https://networkx.github.io/documentation/stable/reference/classes/multidigraph.html) classes

## Metadata

[`d3m.metadata.base`](d3m/metadata/base.py) module provides a standard Python implementation for
metadata object.

When thinking about metadata, it is useful to keep in mind that metadata
can apply to different contexts:
* primitives
* values being passed between primitives, which we call containers (and are container types)
  * datasets are a special case of a container
* to parts of data contained inside a container
  * for example, a cell in a table can have its own metadata

Containers and their data can be seen as multi-dimensional structures.
Dimensions can have numeric (arrays) or string indexes (string to value maps, i.e., dicts).
Moreover, even numeric indexes can still have names associated with each index
value, e.g., column names in a table.

If a container type has a concept of *shape*
([DataFrame](http://pandas.pydata.org/pandas-docs/version/0.17.0/generated/pandas.DataFrame.shape.html),
[ndarray](https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.shape.html)), dimensions go in that order.
For tabular data and existing container types this means that the first dimension of a container is always traversing
samples (e.g., rows in a table), and the second dimension columns.

Values can have nested other values and metadata dimensions go over all of them until scalar values.
So if a Pandas DataFrame contains 3-dimensional ndarrays, the whole value has 5 dimensions: two for rows and columns
of the DataFrame (even if there is only one column), and 3 for the array.

To tell to which part of data contained inside a container metadata applies, we use a *selector*. Selector is a
tuple of strings, integers, or special values. Selector corresponds to a series of `[...]` item getter Python
operations on most values, except for Pandas DataFrame where it corresponds to
[`iloc`](http://pandas.pydata.org/pandas-docs/version/0.17.0/generated/pandas.DataFrame.iloc.html) position-based
selection.

Special selector values:

* `ALL_ELEMENTS` – makes metadata apply to all elements in a given dimension (a wildcard)

Metadata itself is represented as a (potentially nested) dict.
If multiple metadata dicts comes from different selectors for the
same resolved selector location, they are merged together in the order
from least specific to more specific, later overriding earlier.
`null` metadata value clears the key specified from a less specific selector.

### Example

To better understand how metadata is attached to various parts of the value,
A [simple tabular D3M dataset](https://gitlab.com/datadrivendiscovery/tests-data/datasets/iris_dataset_1/)
could be represented as a multi-dimensional structure:

```yaml
{
  "0": [
    [0, 5.1, 3.5, 1.4, 0.2, "Iris-setosa"],
    [1, 4.9, 3, 1.4, 0.2, "Iris-setosa"],
    ...
  ]
}
```

It contains one resource with ID `"0"` which is the first dimension (using strings
as index; it is a map not an array),
then rows, which is the second dimension, and then columns, which is the third
dimension. The last two dimensions are numeric.

In Python, accessing third column of a second row would be
`["0"][1][2]` which would be value `3`. This is also the selector if we
would want to attach metadata to that cell. If this metadata is description
for this cell, we can thus describe this datum metadata as a pair of a selector and
a metadata dict:

* selector: `["0"][1][2]`
* metadata: `{"description": "Measured personally by Ronald Fisher."}`

Dataset-level metadata have empty selector:

* selector: `[]`
* metadata: `{"id": "iris_dataset_1", "name": "Iris Dataset"}`

To describe first dimension itself, we set `dimension` metadata on the dataset-level (container).
`dimension` describes the next dimension at that location in the data structure.

* selector: `[]`
* metadata: `{"dimension": {"name": "resources", "length": 1}}`

This means that the full dataset-level metadata is now:

```json
{
  "id": "iris_dataset_1",
  "name": "Iris Dataset",
  "dimension": {
    "name": "resources",
    "length": 1
  }
}
```

To attach metadata to the first (and only) resource, we can do:

* selector: `["0"]`
* metadata: `{"structural_type": "pandas.core.frame.DataFrame", "dimension": {"length": 150, "name": "rows"}`

`dimension` describes rows.

Columns dimension:

* selector: `["0"][ALL_ELEMENTS]`
* metadata: `{"dimension": {"length": 6, "name": "columns"}}`

Observe that there is no requirement that dimensions are aligned
from the perspective of metadata. But in this case they are, so we can
use `ALL_ELEMENTS` wildcard to describe columns for all rows.

Third column metadata:

* selector: `["0"][ALL_ELEMENTS][2]`
* metadata: `{"name": "sepalWidth", "structural_type": "builtins.str", "semantic_types": ["http://schema.org/Float", "https://metadata.datadrivendiscovery.org/types/Attribute"]}`

Column names belong to each particular column and not all columns.
Using `name` can serve to assign a string name to otherwise numeric dimension.

We attach names and types to datums themselves and not dimensions.
Because we use `ALL_ELEMENTS` selector, this is internally stored efficiently.
We see traditional approach of storing this information in the header of a column
as a special case of a `ALL_ELEMENTS` selector.

Note that the name of a column belongs to the metadata because it is
just an alternative way to reference values in an otherwise numeric
dimension. This is different from a case where a dimension has string-based
index (a map/dict) where names of values are part of the data structure at that
dimension. Which approach is used depends on the structure of the container
for which metadata is attached to.

Default D3M dataset loader found in this package parses all tabular values
as strings and add semantic types, if known, for what could those strings
be representing (a float) and its role (an attribute). This allows primitives
later in a pipeline to convert them to proper structural types but also allows
additional analysis on original values before such conversion is done.

Fetching all metadata for `["0"][1][2]` now returns:

```json
{
  "name": "sepalWidth",
  "structural_type": "builtins.str",
  "semantic_types": [
    "http://schema.org/Float",
    "https://metadata.datadrivendiscovery.org/types/Attribute"
  ],
  "description": "Measured personally by Ronald Fisher."
}
```

### API

[`d3m.metadata.base`](d3m/metadata/base.py) module provides two classes which serve
for storing metadata on values: `DataMetadata` for data values, and `PrimitiveMetadata` for
primitives. It also exposes a `ALL_ELEMENTS` constant to be used in selectors.

You can see public methods available on classes documented in their code. Some main ones are:

* `__init__(metadata)` – constructs a new instance of the metadata class and optionally initializes it with
  top-level metadata
* `update(selector, metadata)` – updates metadata at a given location in data structure
  identified by a selector
* `query(selector)` – retrieves metadata at a given location
* `query_with_exceptions(selector)` – retrieves metadata at a given location, but also returns metadata
  for selectors which have metadata which differs from that of `ALL_ELEMENTS`
* `remove(selector)` – removes metadata at a given location
* `get_elements(selector)` – lists element names which exists at a given location
* `set_for_value(for_value)` – copies metadata and assigns new `for_value` value
* `clear(metadata)` – clears all metadata at all locations, but preserves internal
  link to previous state of metadata
* `to_json()` – converts metadata to a JSON representation
* `pretty_print()` – pretty-print all metadata

`PrimitiveMetadata` differs from `DataMetadata` that it does not accept selector in its
methods because there is no structure in primitives.

Methods accept other arguments as well. Two important ones are `for_value`
and `source`. The former associates metadata with its data value so that
update operations can validate that selectors match existing structure.
`source` records in meta-metadata information who and when was metadata
updated.

### Standard metadata keys

You can use custom keys for metadata, but the following keys are standardized,
so you should use those if you are trying to represent the same metadata:
[`https://metadata.datadrivendiscovery.org/schemas/v0/definitions.json`](https://metadata.datadrivendiscovery.org/schemas/v0/definitions.json) ([source](d3m.metadata/schemas/v0/definitions.json))

The same key always have the same meaning and we reuse the same key
in different contexts when we need the same meaning. So instead of
having both `primitive_name` and `dataset_name` we have just `name`.

Different keys are expected in different contexts:

* `primitive` –
  [`https://metadata.datadrivendiscovery.org/schemas/v0/primitive.json`](https://metadata.datadrivendiscovery.org/schemas/v0/primitive.json) ([source](d3m.metadata/schemas/v0/primitive.json))
* `container` –
  [`https://metadata.datadrivendiscovery.org/schemas/v0/container.json`](https://metadata.datadrivendiscovery.org/schemas/v0/container.json) ([source](d3m.metadata/schemas/v0/container.json))
* `data` –
  [`https://metadata.datadrivendiscovery.org/schemas/v0/data.json`](https://metadata.datadrivendiscovery.org/schemas/v0/data.json) ([source](d3m.metadata/schemas/v0/data.json))

A more user friendly visualizaton of schemas listed above is available at
[https://metadata.datadrivendiscovery.org/](https://metadata.datadrivendiscovery.org/).

Contribute: Standardizing metadata schemas are an ongoing process. Feel free to
contribute suggestions and merge requests with improvements.

### Primitive metadata

Part of primitive metadata can be automatically obtained from primitive's code, some
can be computed through evaluation of primitives, but some has to be provided by
primitive's author. Details of which metadata is currently standardized and what
values are possible can be found in primitive's JSON schema. This section describes
author's metadata into more detail. Example of primitive's metadata provided by an author
from [Monomial test primitive](https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/monomial.py#L32),
slightly modified:

```python
metadata = metadata_module.PrimitiveMetadata({
    'id': '4a0336ae-63b9-4a42-860e-86c5b64afbdd',
    'version': '0.1.0',
    'name': "Monomial Regressor",
    'keywords': ['test primitive'],
    'source': {
        'name': 'Test team',
        'uris': [
            'https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/monomial.py',
            'https://gitlab.com/datadrivendiscovery/tests-data.git',
        ],
    },
    'installation': [{
        'type': metadata_module.PrimitiveInstallationType.PIP,
        'package_uri': 'git+https://gitlab.com/datadrivendiscovery/tests-data.git@{git_commit}#egg=test_primitives&subdirectory=primitives'.format(
            git_commit=utils.current_git_commit(os.path.dirname(__file__)),
        ),
    }],
    'location_uris': [
        'https://gitlab.com/datadrivendiscovery/tests-data/raw/{git_commit}/primitives/test_primitives/monomial.py'.format(
            git_commit=utils.current_git_commit(os.path.dirname(__file__)),
        ),
    ],
    'python_path': 'd3m.primitives.test.MonomialPrimitive',
    'algorithm_types': [
        metadata_module.PrimitiveAlgorithmType.LINEAR_REGRESSION,
    ],
    'primitive_family': metadata_module.PrimitiveFamily.REGRESSION,
})
```

* Primitive's metadata provided by an author is defined as a class attribute and instance of `PrimitiveMetadata`.
* When class is defined, class is automatically analyzed and metadata is extended with automatically
  obtained values from class code.
* `id` can be simply generated using `uuid.uuid4()` in Python and should never change.
  **Do not reuse IDs and do not use the ID from this example.**
* When primitive's code changes you should update the version, a [PEP 440](https://www.python.org/dev/peps/pep-0440/)
  compatible one. Consider updating a version every time you change code, potentially using
  [semantic versioning](https://semver.org/), but nothing of this is enforced.
* `name` is a human-friendly name of the primitive.
* `keywords` can be anything you want to convey to users of the primitive and which could help with
  primitive's discovery.
* `source` describes where the primitive is coming from. The required value is `name` to tell information about the
  author, but you might be interested also in `contact` where you can put an e-mail like `mailto:author@example.com`
  as a way to contact the author. `uris` can be anything. In above, one points to the code in GitLab, and another
  to the repo. If there is a website for the primitive, you might want to add it here as well. These URIs are
  not really meant for automatic consumption but are more as a reference. See `location_uris` for URIs to the code.
* `installation` is important because it describes how can your primitive be automatically installed. Entries are
  installed in order and currently the following types of entries are supported:
  * A `PIP` package available on PyPI or some other package registry:

        ```
        {
          'type': metadata_module.PrimitiveInstallationType.PIP,
          'package': 'my-primitive-package',
          'version': '0.1.0',
        }
        ```

  * A `PIP` package available at some URI. If this is a git repository, then an exact git hash and `egg` name
    should be provided. `egg` name should match the package name installed. Because here we have a chicken
    and an egg problem: how can one commit a hash of code version if this changes the hash, you can use a
    helper utility function to provide you with a hash automatically at runtime. `subdirectory` part of the
    URI suffix is not necessary and is here just because this particular primitive happens to reside in a
    subdirectory of the repository.
  * A `DOCKER` image which should run while the primitive is operating. Starting and stopping of a Docker
    container is managed by a caller, which passes information about running container through primitive's
    `docker_containers` `__init__` argument. The argument is a mapping between the `key` value and address
    and ports at which the running container is available.
    See [Sum test primitive](https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/sum.py#L66)
    for an example:

        ```
        {
            'type': metadata_module.PrimitiveInstallationType.DOCKER,
            'key': 'summing',
            'image_name': 'registry.gitlab.com/datadrivendiscovery/tests-data/summing',
            'image_digest': 'sha256:07db5fef262c1172de5c1db5334944b2f58a679e4bb9ea6232234d71239deb64',
        }
        ```

  * A `UBUNTU` entry can be used to describe a system library or package required for installation or operation
    of your primitive. If your other dependencies require a system library to be installed before they can be
    installed, list this entry before them in `installation` list.

        ```
        {
            'type': metadata_module.PrimitiveInstallationType.UBUNTU,
            'package': 'ffmpeg',
            'version': '7:3.3.4-2',
        }
        ```

  * A `FILE` entry allows a primitive to specify a static file dependency which should be provided by a
    caller to a primitive. Caller passes information about the file path of downloaded file through primitive's
    `volumes` `__init__` argument. The argument is a mapping between the `key` value and file path.
    The filename portion of the provided path does not necessary match the filename portion of the file's URI.

        ```
        {
            'type': metadata_module.PrimitiveInstallationType.FILE,
            'key': 'model',
            'file_uri': 'http://mmlab.ie.cuhk.edu.hk/datasets/comp_cars/googlenet_finetune_web_car_iter_10000.caffemodel',
            'file_digest': '6bdf72f703a504cd02d7c3efc6c67cbbaf506e1cbd9530937db6a698b330242e',
        }
        ```

  * A `TGZ` entry allows a primitive to specify a static directory dependency which should be provided by a
    caller to a primitive. Caller passes information about the directory path of downloaded and extracted file
    through primitive's `volumes` `__init__` argument. The argument is a mapping between the `key` value and
    directory path.

        ```
        {
            'type': metadata_module.PrimitiveInstallationType.TGZ,
            'key': 'mails',
            'file_uri': 'https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz',
            'file_digest': 'b3da1b3fe0369ec3140bb4fbce94702c33b7da810ec15d718b3fadf5cd748ca7',
        }
        ```

* If you can provide, `location_uris` points to an exact code used by the primitive. This can be obtained
  through installing a primitive, but it can be helpful to have an online resource as well.
* `python_path` is a path under which the primitive will get mapped through `setup.py` entry points. This is
  very important to keep in sync.
* `algorithm_types` and `primitive_family` help with discovery of a primitive. They are required and if suitable
  values are not available for you, make a merge request and propose new values. As you see in the code here
  and in `installation` entries, you can use directly Python enumerations to populate these values.

Some other metadata you might be interested to provide to help callers use your primitive better are `preconditions`
(what preconditions should exist on data for primitive to operate well), `effects` (what changes does a primitive
do to data), and a `hyperparams_to_tune` hint to help callers know which hyper-parameters are most important to focus
on.

Primitive metadata also includes descriptions of a primitive and its methods.
These descriptions are automatically obtained from primitive's docstrings.
Docstrings should be made according to
[numpy docstring format](https://numpydoc.readthedocs.io/en/latest/format.html)
([examples](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html)).

### Data metadata

Every value passed around a pipeline has metadata associated with it. Defined container types have an attribute
`metadata` to contain it. API available to manipulate metadata is still evolving because many operations one
can do on data are reasonable also on metadata (e.g., slicing and combining data). Currently, every operation
on data clears and re-initializes associated metadata.

During pipeline construction phase, primitive's `can_accept` method can be called with only metadata for which
resulting metadata should be returned, or `None`. A default implementation provides a very basic metadata
object so consider extending the method and adding more information. For example, if you can know dimensions of
output data based on input data, compute that and add it to resulting metadata. Similarly, if your primitive
accepts different types of inputs but based on a particular input type an output type is known, set structural
type in resulting metadata to that known output type.

>**Note:**
While part of primitive's metadata is obtained automatically nothing like that is currently
done for data metadata. This means one has to manually populate with dimension and typing
information. This will be improved in the future with automatic extraction of this metadata
from data.

## Parameters

A base class to be subclassed and used as a type for `Params` type argument in primitive
interfaces can be found in the [`d3m.metadata.params`](d3m.metadata/params.py) module.
An instance of this subclass should be returned from primitive's ``get_params`` method,
and accepted in ``set_params``.

To define parameters a primitive has you should subclass this base class and define
parameters as class attributes with type annotations. Example:

```python
import numpy
from d3m.metadata import params

class Params(params.Params):
    weights: numpy.ndarray
    bias: float
```

`Params` class is just a fancy Python dict which checks types of parameters and requires
all of them to be set. You can create it like:

```python
ps = Params({'weights': weights, 'bias': 0.1})
ps['bias']
```
```
0.01
```

`weights` and `bias` do not exist as an attributes on the class or instance. In the class
definition, they are just type annotations to configure which parameters are there.

>**Note:**
``Params`` class uses `parameter_name: type` syntax while `Hyperparams` class uses
`hyperparameter_name = Descriptor(...)` syntax. Do not confuse them.

## Hyper-parameters

A base class for hyper-parameters description for primitives can be found in the [`d3m.metadata.hyperparams`](d3m.metadata/hyperparams.py) module.

To define a hyper-parameters space you should subclass this base class and define hyper-parameters
as class attributes. Example:

```python
from d3m.metadata import hyperparams

class Hyperparams(hyperparams.Hyperparams):
    learning_rate = hyperparams.Uniform(lower=0.0, upper=1.0, default=0.001, semantic_types=[
        'https://metadata.datadrivendiscovery.org/types/TuningParameter'
    ])
    clusters = hyperparams.UniformInt(lower=1, upper=100, default=10, semantic_types=[
        'https://metadata.datadrivendiscovery.org/types/TuningParameter'
    ])
```

To access hyper-paramaters space configuration, you can now call:

```python
Hyperparams.configuration
```
```
OrderedDict([('learning_rate', Uniform(lower=0.0, upper=1.0, q=None, default=0.001)), ('clusters', UniformInt(lower=1, upper=100, default=10))])
```

To get a random sample of all hyper-parameters, call:

```python
hp1 = Hyperparams.sample(random_state=42)
```
```
Hyperparams({'learning_rate': 0.3745401188473625, 'clusters': 93})
```

To get an instance with all default values:

```python
hp2 = Hyperparams.defaults()
```
```
Hyperparams({'learning_rate': 0.001, 'clusters': 10})
```

`Hyperparams` class is just a fancy read-only Python dict. You can also manually create its instance:

```python
hp3 = Hyperparams({'learning_rate': 0.01, 'clusters': 20})
hp3['learning_rate']
```
```
0.01
```

If you want to use most of default values, but set some, you can thus use this dict-construction approach:

```python
hp4 = Hyperparams(Hyperparams.defaults(), clusters=30)
```
```
Hyperparams({'learning_rate': 0.001, 'clusters': 30})
```

There is no class- or instance-level attribute `learning_rate` or `clusters`. In the class definition, they were
used only for defining the hyper-parameters space, but those attributes were extracted out and put into
`configuration` attribute.

There are four types of hyper-parameters:
 * tuning parameters which should be tuned during hyper-parameter optimization phase
 * control parameters which should be determined during pipeline construction phase and
   are part of the logic of the pipeline
 * parameters which control the use of resources by the primitive
 * parameters which control which meta-features are computed by the primitive

You can use hyper-parameter's semantic type to differentiate between those types of
hyper-parameters using the following URIs:
 * `https://metadata.datadrivendiscovery.org/types/TuningParameter`
 * `https://metadata.datadrivendiscovery.org/types/ControlParameter`
 * `https://metadata.datadrivendiscovery.org/types/ResourcesUseParameter`
 * `https://metadata.datadrivendiscovery.org/types/MetafeatureParameter`

Once you define a `Hyperparams` class for your primitive you can pass it as a
class type argument in your primitive's class definition:

```python
class MyPrimitive(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    ...
```

Those class type arguments are then automatically extracted from the class definition
and made part of primitive's metadata. This allows the caller to access the `Hyperparams`
class to crete an instance to pass to primitive's constructor:

```python
hyperparams_class = MyPrimitive.metadata.query()['primitive_code']['class_type_arguments']['Hyperparams']
primitive = MyPrimitive(hyperparams=hyperparams_class.defaults())
```

>**Note:**
`Hyperparams` class uses `hyperparameter_name = Descriptor(...)` syntax  while ``Params`` class
uses `parameter_name: type` syntax. Do not confuse them.

## Problem description

[`d3m.metadata.problem`](d3m.metadata/problem.py) module provides a parser for problem description into a normalized Python object.

You can load a problem description and get the loaded object dumped back by running:

```bash
python -m d3m.metadata.problem <path to problemDoc.json>
```

## Dataset

This package also provides a Python class to load and represent datasets in Python in [`d3m.container.dataset`](d3m/container/dataset.py)
module. This container value can serve as an input to the whole pipeline and be used as input for primitives which operate on a
dataset as a whole. It allows one to register multiple loaders to support different formats of datasets. You pass an URI to
a dataset and it automatically picks the right loader. By default it supports:

* D3M dataset. Only `file://` URI scheme is supported and URI should point to the `datasetDoc.json` file. Example: `file:///path/to/datasetDoc.json`
* CSV file. Many URI schemes are supported, including remote ones like `http://`. URI should point to a
  file with `.csv` extension. Example: `http://example.com/iris.csv`
* Sklearn [example datasets](http://scikit-learn.org/stable/modules/classes.html#module-sklearn.datasets). Example: `sklearn://boston`

You can load a dataset and get the loaded object dumped back by running:

```bash
python -m d3m.container.dataset <path to the dataset file>
```
# Python interfaces for TA1 primitives

A collection of standard Python interfaces for TA1 primitives. All primitives should
extend one of the base classes available and optionally implement available mixins.

## Design principles

Standard TA1 primitive interfaces have been designed to be possible for TA2 systems to call
primitives automatically and combine them into pipelines.

Some design principles applied:

* Use of a de facto standard language for "glue" between different components and libraries,
  Python.
* Use of keyword-only arguments for all methods so that caller does not have to worry
  about the order of arguments.
* Every primitive should implement only one functionality, more or less a function, with clear
  inputs and outputs. All parameters of the function do not have to be known in advance and function
  can be "fitted" as part of the training step of the pipeline.
* Use of Python 3 typing extensions to annotate methods and classes with typing information
  to make it easier for TA2 systems to prune incompatible combinations of inputs and outputs
  and to reuse existing Python type-checking tooling.
* Typing information can serve both detecting issues and incompatibilities in primitive
  implementations and help with pipeline construction.
* All values being passed through a primitive have metadata associated with them.
* Primitives can operate only at a metadata level to help guide the pipeline construction
  process without having to operate on data itself.
* Primitive metadata is close to the source, primitive code, and not in separate files to minimize
  chances that it is goes out of sync. Metadata which can be automatically determined from the
  code should be automatically determined from the code. Similarly for data metadata.
* All randomness of primitives is captured by a random seed argument to assure reproducibility.
* Operations can work in iterations, under time budgets, and caller might not always want to
  compute values fully.
* Through use of mixins primitives can signal which capabilities they support.
* Primitives are to be composed and executed in a data-flow manner.

## Main concepts

Interface classes, mixins, and methods are documented in detail through use of docstrings and
typing annotations. Here we note some higher-level concept which can help understand basic
ideas behind interfaces and what they are trying to achieve, the big picture. This section
is not normative.

A primitive should extend one of the base classes available and optionally mixins as well.
Not all mixins apply to all primitives. That being said, you probably do not want to
subclass `PrimitiveBase` directly, but instead one of other base classes to signal to
a caller more about what your primitive is doing. If your primitive belong to a larger
set of primitives no exiting non-`PrimitiveBase` base class suits well, consider suggesting
that a new base class is created by opening an issue or making a merge request.

Base class and mixins have generally four type arguments you have to provide: `Inputs`,
`Outpus`, `Params`, and `Hyperparams`. One can see a primitive as parameterized by those
four type arguments. You can access them at runtime through metadata:

```python
FooBarPrimitive.metadata.query()['class_type_arguments']
```

`Inputs` should be set to a primary input type of a primitive. Primary, because you can
define additional inputs your primitive might need, but we will go into these details later.
Similarly for `Outputs`. `produce` method then produces outputs from inputs. Other primitive
methods help the primitive (and its `produce` method) achieve that, or help the runtime execute
the primitive as a whole, or optimize its behavior.

Both `Inputs` and `Outputs` should be of a
[standard container data type](https://gitlab.com/datadrivendiscovery/d3m#container-types).
We allow a limited set of value types being passed between primitives so that both TA2 and TA3
systems can implement introspection for those values if needed, or user interface for them, etc.
Moreover this allows us also to assure that they can be efficiently used with
Arrow/Plasma store.

Container values can then in turn contain values of
an [extended but still limited set of data types](https://gitlab.com/datadrivendiscovery/d3m#data-types).

Those values being passed between primitives also hold metadata. Metadata is available on
their `metadata` attribute. Metadata on values is stored in an instance of
[`DataMetadata`](https://gitlab.com/datadrivendiscovery/d3m/blob/master/d3m/metadata/metadata.py)
class. This is a reason why we have
[our own versions of some standard container types](https://gitlab.com/datadrivendiscovery/d3m/tree/master/d3m/container):
to have the `metadata` attribute.

All metadata is immutable and updating a metadata object returns a new, updated, copy.
Metadata internally remembers the history of changes, but there is no API yet to access that.
But the idea is that you will be able to follow the whole history of change to data in a pipeline
through metadata. See [metadata API](https://gitlab.com/datadrivendiscovery/d3m#api) for
more information how to manipulate metadata.

Primitives have a similar class `PrimitiveMetadata`, which when created automatically analyses
its primitive and populates parts of metadata based on that. In this way author does not have
to have information in two places (metadata and code) but just in code and metadata is extracted
from it. When possible. Some metadata author of the primitive stil has to provide directly.

Currently most standard interface base classes have only one `produce` method, but design
allows for multiple: their name has to be prefixed with `produce_`, have similar arguments
and same semantics as all produce methods. The main motivation for this is that some primitives
might be able to expose same results in different ways. Having multiple produce methods
allow the caller to pick which type of the result they want.

To keep primitive from outside simple and allow easier compositionality in pipelines, primitives
have arguments defined per primitive and not per their method. The idea here is that once a
caller satisfies (computes a value to be passed to) an argument, any method which requires
that argument can be called on a primitive.

There are three types of arguments:

* pipeline – arguments which are provided by the pipeline, they are required (otherwise caller would be able to trivially satisfy them by
  always passing `None` or another default value)
* runtime – arguments which caller provides during pipeline execution and they control
  various aspects of the execution
* hyper-parameter – a method can declare that primitive's hyper-parameter can be overridden for
  the call of the method, they have to match hyper-parameter definition

Methods can accept additional pipeline and hyper-parameter arguments and not just those from the
standard interfaces.

Because methods can accept additional arguments and because structural types are not enough
in many cases to know if a value is a good for a particular argument, there is a
`can_accept` class method which primitives can override to give the caller feedback in advance,
before the pipeline itself is already running. Default implementation jut checks structural
typing information and passes outputs structural typing information on, but ideally this
class method should check much more: shapes, dimensions, types of internal data structures, etc.
For example, the fact that inputs are a numpy array does not help much to know which value
to bring as inputs, because numpy array structural type does not cary enough information.
But metadata associated with values hopefully does.

Produce methods and some other methods return results wrapped in `CallResult`. In this way
primitives can expose information about internal iterative or optimization process and
allow caller to decide how long to run.

When calling a primitive, to access `Hyperparams` class you can do:

```python
hyperparams_class = FooBarPrimitive.metadata.query()['class_type_arguments']['Hyperparams']
```

You can now create an instance of the class by directly providing values for hyper-parameters,
use available simple sampling, or just use default values:

```python
hp1 = hyperparams_class({'threshold': 0.01})
hp2 = hyperparams_class.sample(random_state=42)
hp3 = hyperparams_class.defaults
```

You can then pass those instances as the `hyperparams` argument to primitive's constructor.

Author of a primitive has to define what internal parameters does the primitive have, if
any, by extending the `Params` class. It is just a fancy dict, so you can both create
an instance of it in the same way, and access its values:

```python
class Params(params.Params):
    coefficients: numpy.ndarray

ps = Params({'coefficients': numpy.array[1, 2, 3]})
ps['coefficients']
```

`Hyperparams` class and `Params` class have to be pickable and copyable so that instances
of primitives can be serialized and restored as needed.

Primitives (and some other values) are uniquely identified by their ID and version.
ID does not change through versions.

Primitives should not modify in-place any input argument but always first make a copy
before any modification.

# Pipeline

Pipeline is described as a DAG consisting of interconnected steps, where steps can be primitives,
or (nested) other pipelines. Pipeline has data-flow semantics, which means that steps
are not necessary executed in the order they are listed, but a step can be executed when all its
inputs are available. Some steps can even be executed in parallel. On the other hand,
each step can use only previously defined outputs from steps coming before in the order
they are listed. In JSON, the following is a sketch of its representation:

```yaml
{
  "id": <UUID of the pipeline>,
  "schema": <a URI representing a schema and version to which pipeline description conforms>,
  "source": {
    "name": <string representing name of the author, team>,
    "contact": <contact information of author of the pipeline>,
    "from": <if pipeline was derived from another pipeline, or pipelines, which>
    ... # Any extra metadata author might want to add into the pipeline, like version,
        # name, and config parameters of the system which produced this pipeline.
  },
  "created": <timestamp when created>,
  "context": <"PRETRAINING", "TESTING", "EVALUATION", "PRODUCTION">, # In which context was the pipeline created?
  "name": <human friendly name of the pipeline, if it exists>,
  "description": <human friendly description of the pipeline, if it exists>,
  "users": [
    {
      "id": <UUID for the user, if user is associated with the creation of the pipeline>,
      "reason": <textual description of what user did to create the pipeline>,
      "rationale": <textual description by the user of what the user did>
    }
  ],
  "inputs": [
    {
      "name": <human friendly name of the inputs>
    }
  ],
  "outputs": [
    {
      "name": <human friendly name of the outputs>,
      "data": <data reference, probably of an output of a step>
    }
  ],
  "steps": [
    {
      "type": "PRIMITIVE",
      "primitive": {
        "id": <ID of the primitive used in this step>,
        "version": <version of the primitive used in this step>,
        "python_path": <Python path of this primitive>,
        "name": <human friendly name of this primitive>,
        "digest": <digest of this primitive>
      },
      # Constructor arguments should not be listed here, because they can be automatically created from other
      # information. All these arguments are listed as kind "PIPELINE" in primitive's metadata.
      "arguments": {
         # A standard inputs argument used for both set_training_data and default "produce" method.
        "inputs": {
          "type": "CONTAINER",
          "data": <data reference, probably of an output of a step or pipeline input>
        },
         # A standard inputs argument, used for "set_training_data".
        "outputs": {
          "type": "CONTAINER",
          "data": <data reference, probably of an output of a step or pipeline input>
        },
        # An extra argument which takes as inputs outputs from another primitive in this pipeline.
        "extra_data": {
          "type": "CONTAINER",
          "data": <data reference, probably of an output of a step or pipeline input>
        },
        # An extra argument which takes as input a singleton output from another step in this pipeline.
        "offset": {
          "type": "DATA",
          "data": <data reference, probably of an output of a step or pipeline input>
        }
      },
      "outputs": [
        {
          # Data is made available by this step from default "produce" method.
          "id": "produce"
        },
        {
          # Data is made available by this step from an extra "produce" method, too.
          "id": "produce_score"
        }
      ],
      # Some hyper-parameters are not really tunable and should be fixed as part of pipeline definition. This
      # can be done here. Hyper-parameters listed here cannot be tuned or overridden during a run. Author of
      # a pipeline decides which hyper-parameters are which, probably based on their semantic type.
      # This is a map hyper-parameter names and their values using a similar format as arguments, but
      # allowing also PRIMITIVE and VALUE types.
      "hyperparams": {
        "loss": {
          "type": "PRIMITIVE",
          "data": <0-based index from steps identifying a primitive to pass in>
        },
        "column_to_operate_on": {
          "type": "VALUE",
          # Value is converted to a JSON-compatible value by hyper-parameter class.
          # It also knows how to convert it back.
          "data": 5
        },
        # A special case where a hyper-parameter can also be a list of primitives,
        # which are then passed to the \"Set\" hyper-parameter class.
        "ensemble": {
          "type": "PRIMITIVE",
          "data": [
            <0-based index from steps identifying a primitive to pass in>,
            <0-based index from steps identifying a primitive to pass in>
          ]
        }
      },
      "users": [
        {
          "id": <UUID for the user, if user is associated with selection of this primitive/arguments/hyper-parameters>,
          "reason": <textual description of what user did to select this primitive>,
          "rationale": <textual description by the user of what the user did>
        }
      ]
    },
    {
      "type": "SUBPIPELINE",
      "pipeline": {
        "id": <UUID of a pipeline to run as this step>
      },
      # For example: [{"data": "steps.0.produce"}] would map the data reference "steps.0.produce" of
      # the outer pipeline to the first input of a sub-pipeline.
      "inputs": [
        {
          "data": <data reference, probably of an output of a step or pipeline input, mapped to sub-pipeline's inputs in order>
        }
      ],
      # For example: [{"id": "predictions"}] would map the first output of a sub-pipeline to a data
      # reference "steps.X.predictions" where "X" is the step number of a given sub-pipeline step.
      "outputs": [
        {
          "id": <ID to be used in data reference, mapping sub-pipeline's outputs in order>
        }
      ]
    },
    {
      # Used to represent a pipeline template which can be used to generate full pipelines. Not to be used in
      # the metalearning context. Additional properties to further specify the placeholder constraints are allowed.
      "type": "PLACEHOLDER",
      # A list of inputs which can be used as inputs to resulting sub-pipeline.
      # Resulting sub-pipeline does not have to use all the inputs, but it cannot use any other inputs.
      "inputs": [
        {
          "data": <data reference, probably of an output of a step or pipeline input>
        }
      ],
      # A list of outputs of the resulting sub-pipeline.
      # Their (allowed) number and meaning are defined elsewhere.
      "outputs": [
        {
          "id": <ID to be used in data reference, mapping resulting sub-pipeline's outputs in order>
        }
      ]
    }
  ]
}
```

`id` uniquely identifies this particular database document.

Pipeline describes how inputs are computed into outputs. In most cases inputs are
[Dataset container values](./d3m/container/dataset.py) and outputs are predictions as
[Pandas dataframe container values](./d3m/container/pandas.py)
in [Lincoln Labs predictions format](https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/blob/shared/documentation/problemSchema.md#predictions-file),
and, during training, potentially also internal losses/scores. The same pipeline is used for both training and predicting.

Pipeline description contains many *data references*. Data reference is just a string
which identifies an output of a step or a pipeline input and forms a data-flow connection
between data available and an input to a step. It is recommended to be a string of the
following forms:

 * `steps.<number>.<id>` — `number` identifies the step in the list of steps (0-based)
   and `id` identifies the name of a produce method of the primitive,
   or the output of a pipeline step
 * `inputs.<number>` — `number` identifies the pipeline input (0-based)
 * `outputs.<number>` — `number` identifies the pipeline output (0-based)

Inputs in the context of metalearning are expected to be datasets, and the order of inputs
match the order of datasets in a pipeline run. (In other contexts, like TA2-TA3 API, inputs
might be something else, for example a pipeline can consist of just one primitive a TA3
wants to run on a particular input.)

Remember that each primitive has a set of arguments it takes as a whole, combining all the
arguments from all its methods. Each argument (identified by its name) can have only one
value associated with it and any method accepting that argument receives that value. Once
all values for all arguments for a method are available, that method can be called.

Remember as well that each primitive can have multiple "produce" methods. These methods can
be called after a primitive has been fitted. In this way a primitive can have multiple outputs,
for each "produce" method one.

Placeholders can be used to define pipeline templates to be used outside of the metalearning
context. A placeholder is replaced with a pipeline step to form a pipeline. Restrictions
of placeholders may apply on the number of them, their position, allowed inputs and outputs,
etc.

# Examples

Examples of simple primitives using these interfaces can be found
[in this repository](https://gitlab.com/datadrivendiscovery/tests-data/tree/master/primitives):

* [MonomialPrimitive](https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/monomial.py)
  is a simple regressor which shows how to use `container.List`, define and use `Params`
  and `Hyperparams`, and implement multiple methods needed by a supervised learner primitive
* [IncrementPrimitive](https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/increment.py)
  is a transformer and shows how to have `container.ndarray` as inputs and outputs, how to set metadata for outputs,
  and how to extend `can_accept` to check if inputs have the right structure and types
  because `container.ndarray` does not expose those details through its structural type,
  but inputs' metadata provides it
* [SumPrimitive](https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/sum.py)
  is a transformer as well, but it is just a wrapper around a Docker image, it shows how
  to define Docker image in metadata and how to connect to a running Docker container,
  moreover, it also shows how inputs can be a union type of multiple other types
* [RandomPrimitive](https://gitlab.com/datadrivendiscovery/tests-data/blob/master/primitives/test_primitives/random.py)
  is a generator which shows how to use `random_seed`, too.

import abc
import base64
import collections
import contextlib
import datetime
import decimal
import enum
import inspect
import json
import logging
import numbers
import os
import types
import typing
import sys
import unittest

import custom_inherit  # type: ignore
import frozendict  # type: ignore
import git  # type: ignore
import jsonpath_ng  # type: ignore
import jsonschema  # type: ignore
import numpy  # type: ignore
import pandas  # type: ignore
import typing_inspect  # type: ignore
import yaml  # type: ignore
from pytypes import type_util  # type: ignore

from d3m import exceptions

# None is not allowed because we are using it to signal a removal of metadata in update.
KNOWN_IMMUTABLE_TYPES = (
    bool, numbers.Integral, numbers.Complex, decimal.Decimal, numbers.Real,
    numpy.integer, numpy.float64, str, bytes,
    datetime.date, datetime.time, datetime.datetime, type(None), enum.Enum,
)


def current_git_commit(path: str) -> str:
    """
    Returns a git commit hash of the repo at or above ``path``.

    When used to get a commit hash of a Python package, for this to work, the package has
    to be installed in "editable" mode (``pip install -e``).

    Parameters
    ----------
    path : str
        A path to repo or somewhere under the repo.

    Returns
    -------
    str
        A git commit hash.
    """

    repo = git.Repo(path=path, search_parent_directories=True)
    return repo.head.object.hexsha


# Using typing.TypeVar in type signature does not really work, so we are using type instead.
# See: https://github.com/python/typing/issues/520
def get_type_arguments(cls: type, *, unique_names: bool = False) -> typing.Dict[type, type]:
    """
    Returns a mapping between type arguments and their types of a given class ``cls``.

    Parameters
    ----------
    cls : type
        A class to return mapping for.
    unique_names : bool
        Should we force unique names of type parameters.

    Returns
    -------
    Dict[TypeVar, type]
        A mapping from type argument to its type.
    """

    # Using typing.TypeVar in type signature does not really work, so we are using type instead.
    # See: https://github.com/python/typing/issues/520
    result: typing.Dict[type, type] = {}

    for base_class in inspect.getmro(typing_inspect.get_origin(cls)):
        if base_class == typing.Generic:
            break

        if not typing_inspect.is_generic_type(base_class):
            continue

        parameters = typing_inspect.get_parameters(base_class)

        # We are using _select_Generic_superclass_parameters and not get_Generic_parameters
        # so that we can handle the case where the result is None.
        # See: https://github.com/Stewori/pytypes/issues/20
        arguments = type_util._select_Generic_superclass_parameters(cls, base_class)

        if arguments is None:
            arguments = [typing.Any] * len(parameters)

        if len(parameters) != len(arguments):
            raise TypeError("Number of parameters does not match number of arguments.")

        for parameter, argument in zip(parameters, arguments):
            if type_util.resolve_fw_decl(argument, module_name=base_class.__module__, globs=dir(sys.modules[base_class.__module__]))[1]:
                argument = argument.__forward_value__

            visited: typing.Set[type] = set()
            while typing_inspect.is_typevar(argument) and argument in result:
                if argument in visited:
                    raise RuntimeError("Loop while resolving type variables.")
                visited.add(argument)

                argument = result[argument]

            if parameter == argument:
                argument = typing.Any

            if parameter in result:
                if result[parameter] != argument:
                    raise TypeError("Different types for same parameter across class bases: {type1} vs. {type2}".format(
                        type1=result[parameter],
                        type2=argument,
                    ))
            else:
                result[parameter] = argument

    if unique_names:
        type_parameter_names = [parameter.__name__ for parameter in result.keys()]

        type_parameter_names_set = set(type_parameter_names)

        if len(type_parameter_names) != len(type_parameter_names_set):
            for name in type_parameter_names_set:
                type_parameter_names.remove(name)
            raise TypeError("Same name reused across different type parameters: {extra_names}".format(extra_names=type_parameter_names))

    return result


def is_instance(obj: typing.Any, cls: typing.Union[type, typing.Tuple[type]]) -> bool:
    # We do not want really to check generators. A workaround.
    # See: https://github.com/Stewori/pytypes/issues/49
    if isinstance(obj, types.GeneratorType):
        return False

    if isinstance(cls, tuple):
        cls = typing.Union[cls]  # type: ignore

    # "bound_typevars" argument has to be passed for this function to
    # correctly work with type variables.
    # See: https://github.com/Stewori/pytypes/issues/24
    return type_util._issubclass(type_util.deep_type(obj), cls, bound_typevars={})


def is_subclass(subclass: type, superclass: typing.Union[type, typing.Tuple[type]]) -> bool:
    # "bound_typevars" argument has to be passed for this function to
    # correctly work with type variables.
    # See: https://github.com/Stewori/pytypes/issues/24
    return type_util._issubclass(subclass, superclass, bound_typevars={})


def get_type(obj: typing.Any) -> type:
    typ = type_util.deep_type(obj, depth=1)

    if is_subclass(typ, type_util.Empty):
        typ = typing_inspect.get_last_args(typ)[0]

    return typ


def is_instance_method_on_class(method: typing.Any) -> bool:
    if is_class_method_on_class(method):
        return False

    if inspect.isfunction(method):
        return True

    if getattr(method, '__func__', None):
        return True

    return False


def is_class_method_on_class(method: typing.Any) -> bool:
    return inspect.ismethod(method)


def is_instance_method_on_object(method: typing.Any, object: typing.Any) -> bool:
    if not inspect.ismethod(method):
        return False

    if method.__self__ is object:
        return True

    return False


def is_class_method_on_object(method: typing.Any, object: typing.Any) -> bool:
    if not inspect.ismethod(method):
        return False

    if method.__self__ is type(object):
        return True

    return False


def is_type(obj: typing.Any) -> bool:
    return isinstance(obj, type) or typing_inspect.is_tuple_type(obj) or typing_inspect.is_union_type(obj)


class EnumMeta(enum.EnumMeta):
    def __new__(mcls, class_name, bases, namespace, **kwargs):  # type: ignore
        cls = super().__new__(mcls, class_name, bases, namespace, **kwargs)

        def yaml_representer(dumper, data):  # type: ignore
            return yaml.ScalarNode('tag:yaml.org,2002:str', data.name)

        yaml.add_representer(cls, yaml_representer)

        return cls


class Enum(enum.Enum, metaclass=EnumMeta):
    """
    An implementation of `Enum` base class whose instances are equal to their string names, too.

    Moreover, it registers itself with "yaml" module to serialize itself as a string.
    """

    def __eq__(self, other):  # type: ignore
        if isinstance(other, str):
            return self.name == other

        return super().__eq__(other)

    # It must hold a == b => hash(a) == hash(b). Because we allow enums to be equal to names,
    # the easiest way to assure the condition is to hash everything according to their names.
    def __hash__(self):  # type: ignore
        return hash(self.name)


# Return type has to be "Any" because mypy does not support enums generated dynamically
# and complains about missing attributes when trying to access them.
def create_enum_from_json_schema_enum(class_name: str, obj: typing.Dict, json_path: str, *, module: str = None, qualname: str = None, base_class: type = None) -> typing.Any:
    if qualname is None:
        qualname = class_name

    json_path_expression = jsonpath_ng.parse(json_path)

    names = [match.value for match in json_path_expression.find(obj)]

    # Make the list contain unique names. It works in Python 3.6+ because dicts are ordered.
    names = list(dict.fromkeys(names))

    return Enum(value=class_name, names=names, start=1, module=module, qualname=qualname, type=base_class)  # type: ignore


def make_immutable_copy(obj: typing.Any, _path: typing.List[typing.Any] = None) -> typing.Any:
    """
    Converts a given ``obj`` into an immutable copy of it, if possible.

    Parameters
    ----------
    obj : any
        Object to convert.
    _path : list(any)
        Current path during ``obj`` traversal.

    Returns
    -------
    any
        An immutable copy of ``obj``.
    """

    # Importing here to prevent import cycle.
    from d3m.metadata import base as metadata_base
    from d3m.primitive_interfaces import base

    if _path is None:
        _path = [obj]

    if isinstance(obj, numpy.matrix):
        # One cannot iterate over a matrix segment by segment. You always get back
        # a matrix (2D structure) and not an array of rows or columns. By converting
        # it to an array such iteration segment by segment works.
        obj = numpy.array(obj)

    if isinstance(obj, KNOWN_IMMUTABLE_TYPES):
        # Because str is among known immutable types, it will not be picked apart as a sequence.
        return obj
    if obj is metadata_base.ALL_ELEMENTS or obj is metadata_base.NO_VALUE:
        return obj
    if is_type(obj):
        # Assume all types are immutable.
        return obj
    if isinstance(obj, typing.Mapping):
        # We simply always preserve order of the mapping. Because we want to make sure also mapping's
        # values are converted to immutable values, we cannot simply use MappingProxyType.
        return frozendict.FrozenOrderedDict((make_immutable_copy(k, _path + [k]), make_immutable_copy(v, _path + [k])) for k, v in obj.items())
    if isinstance(obj, typing.Set):
        return frozenset(make_immutable_copy(o, _path + [o]) for o in obj)
    if isinstance(obj, tuple):
        # To preserve named tuples.
        return type(obj)(make_immutable_copy(o, _path + [o]) for o in obj)
    if isinstance(obj, pandas.DataFrame):
        return tuple(make_immutable_copy(o, _path + [o]) for o in obj.itertuples(index=False, name=None))
    if isinstance(obj, typing.Sequence):
        return tuple(make_immutable_copy(o, _path + [o]) for o in obj)
    if isinstance(obj, base.PrimitiveBase):
        # This is a tricky one. Primitive instances are generally mutable, they can change state when they are used.
        # But as part of hyper-parameters, they can be used as instances and are seen as immutable because the idea
        # is that TA2 will make a copy of the primitive before passing it in as a hyper-parameter, leaving initial
        # instance intact.
        return obj

    raise TypeError("{obj} at {path} is not known to be immutable.".format(obj=obj, path=_path))


class Metaclass(custom_inherit._DocInheritorBase):
    """
    A metaclass which makes sure docstrings are inherited.

    It knows how to merge numpy-style docstrings and merge parent sections with
    child sections. For example, then it is not necessary to repeat documentation
    for parameters if they have not changed.
    """

    @staticmethod
    def class_doc_inherit(prnt_doc: str = None, child_doc: str = None) -> typing.Optional[str]:
        return custom_inherit.store['numpy'](prnt_doc, child_doc)

    @staticmethod
    def attr_doc_inherit(prnt_doc: str = None, child_doc: str = None) -> typing.Optional[str]:
        return custom_inherit.store['numpy'](prnt_doc, child_doc)


class AbstractMetaclass(abc.ABCMeta, Metaclass):
    """
    A metaclass which makes sure docstrings are inherited. For use with abstract classes.
    """


class GenericMetaclass(typing.GenericMeta, Metaclass):
    """
    A metaclass which makes sure docstrings are inherited. For use with generic classes (which are also abstract).
    """


class RefResolverNoRemote(jsonschema.RefResolver):
    def resolve_remote(self, uri: str) -> typing.Any:
        raise exceptions.NotSupportedError("Remote resolving disabled: {uri}".format(uri=uri))


def enum_validator(validator, enums, instance, schema):  # type: ignore
    if isinstance(instance, Enum):
        instance = instance.name

    yield from jsonschema.Draft4Validator.VALIDATORS['enum'](validator, enums, instance, schema)


class Draft4Validator(jsonschema.Draft4Validator):
    """
    JSON schema validator with the following extensions:

    * Support for type "type" which succeeds if the value is a a Python type.
    * If a value is an instance of Python enumeration, its name is checked against JSON
      schema enumeration, instead of the vaule itself.

    When converting to a proper JSON these values validated under extensions should be
    converted to a stringified values (stringified Python type or enumeration's name),
    but which will then not validate anymore against the JSON schema.
    """

    VALIDATORS = dict(jsonschema.Draft4Validator.VALIDATORS, **{
        'enum': enum_validator,
    })

    def is_type(self, instance: typing.Any, type: type) -> bool:
        if type == 'type':
            return is_type(instance)
        elif type == 'string' and isinstance(instance, Enum):
            return True
        else:
            return super().is_type(instance, type)


def load_schema_validators(schemas_path: str, definitions_json: typing.Dict, schemas: typing.Sequence[str]) -> typing.List[Draft4Validator]:
    validators = []

    for schema_filename in schemas:
        with open(os.path.join(schemas_path, schema_filename), 'r') as schema_file:
            schema_json = json.load(schema_file)

        Draft4Validator.check_schema(schema_json)

        validator = Draft4Validator(
            schema=schema_json,
            types=dict(Draft4Validator.DEFAULT_TYPES, **{
                'array': (list, tuple, set),
                'object': (dict, frozendict.frozendict, frozendict.FrozenOrderedDict),
            }),
            resolver=RefResolverNoRemote(schema_json['id'], schema_json, {
                'https://metadata.datadrivendiscovery.org/schemas/v0/definitions.json': definitions_json,
            }),
            format_checker=jsonschema.draft4_format_checker,
        )

        validators.append(validator)

    return validators


class JsonEncoder(json.JSONEncoder):
    """
    JSON encoder with extensions, among them the main ones are:

    * Frozen dict is encoded as a dict.
    * Python types are encoded into strings describing them.
    * Python enumerations are encoded into their string names.
    * Sets are encoded into lists.
    * Encodes ndarray and DataFrame as nested lists.
    * Encodes datetime into ISO format with UTC timezone.
    * Everything else which cannot be encoded is converted to a string.
    """

    def default(self, o: typing.Any) -> typing.Any:
        # Importing here to prevent import cycle.
        from d3m.metadata import base

        if isinstance(o, numpy.matrix):
            # One cannot iterate over a matrix segment by segment. You always get back
            # a matrix (2D structure) and not an array of rows or columns. By converting
            # it to an array such iteration segment by segment works.
            o = numpy.array(o)

        if isinstance(o, frozendict.frozendict):
            return dict(o)
        if isinstance(o, frozendict.FrozenOrderedDict):
            return collections.OrderedDict(o)
        if is_type(o):
            return type_util.type_str(o, assumed_globals={}, update_assumed_globals=False)
        if isinstance(o, Enum):
            return o.name
        if o is base.ALL_ELEMENTS:
            return repr(o)
        if o is base.NO_VALUE:
            return repr(o)
        # For encoding numpy.int64. numpy.float64 already works.
        if isinstance(o, numpy.integer):
            return int(o)
        if isinstance(o, typing.Mapping):
            return collections.OrderedDict(o)
        if isinstance(o, typing.Set):
            return sorted(o, key=str)
        if isinstance(o, pandas.DataFrame):
            return list(o.itertuples(index=False, name=None))
        if isinstance(o, typing.Sequence):
            return list(o)
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, bytes):
            return base64.b64encode(o).decode('utf8')
        if isinstance(o, datetime.datetime):
            # Since Python 3.6 "astimezone" can be called on naive instances
            # that are presumed to represent system local time.
            # We remove timezone information before formatting to not have "+00:00" added and
            # we then manually add "Z" instead (which has equivalent meaning).
            return o.astimezone(datetime.timezone.utc).replace(tzinfo=None).isoformat('T') + 'Z'

        try:
            return super().default(o)
        except TypeError:
            return str(o)


def to_json_structure(obj: typing.Any) -> typing.Any:
    # TODO: Is there a better way to trigger a run of JsonEncoder recursively without going to a string?
    return json.loads(json.dumps(obj, cls=JsonEncoder))


class StreamToLogger:
    def __init__(self, logger: logging.Logger, level: typing.Union[str, int]) -> None:
        self.logger = logger
        self.level = logging._checkLevel(level)  # type: ignore
        self.closed = False

    def write(self, buffer: str) -> int:
        if self.closed:
            raise ValueError("Stream is closed.")

        for line in buffer.splitlines():
            line = line.strip()
            if line:
                self.logger.log(self.level, line)

        return len(buffer)

    def writelines(self, lines: typing.List[str]) -> None:
        if self.closed:
            raise ValueError("Stream is closed.")

        for line in lines:
            line = line.strip()
            if line:
                self.logger.log(self.level, line)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    def seekable(self) -> bool:
        return False

    def seek(self, offset: int, whence: int = 0) -> int:
        raise OSError("Stream is not seekable.")

    def tell(self) -> int:
        raise OSError("Stream is not seekable.")

    def truncate(self, size: int = None) -> int:
        raise OSError("Stream is not seekable.")

    def writable(self) -> bool:
        return True

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        return False

    def read(self, n: int = -1) -> typing.AnyStr:
        raise OSError("Stream is write-only.")

    def readline(self, limit: int = -1) -> typing.AnyStr:
        raise OSError("Stream is write-only.")

    def readlines(self, hint: int = -1) -> typing.List[typing.AnyStr]:
        raise OSError("Stream is write-only.")

    def fileno(self) -> int:
        raise OSError("Stream does not use a file descriptor.")


class redirect_to_logging(contextlib.AbstractContextManager):
    """
    A Python context manager which redirects all writes to stdout and stderr
    to Python logging.

    Primitives should use logging to log messages, but maybe they are not doing
    that or there are other libraries they are using which are not doing that.
    One can then use this context manager to assure that (at least all Python)
    writes to stdout and stderr by primitives are redirected to logging::

        with redirect_to_logging(logger=PrimitiveClass.logger):
            primitive = PrimitiveClass(...)
            primitive.set_training_data(...)
            primitive.fit(...)
            primitive.produce(...)

    If you are using `logging.StreamHandler` in your logging configuration (e.g., to
    output logging to a console), it is important that you configure it before
    using this context manager so that initial stderr is stored by the handler,
    before the context manager swaps it. Otherwise you will get into a recursive loop.
    """

    def __init__(self, logger: logging.Logger = None, stdout_level: typing.Union[int, str] = 'INFO', stderr_level: typing.Union[int, str] = 'ERROR') -> None:
        if logger is None:
            self.logger = logging.getLogger('redirect')
        else:
            self.logger = logger

        self.stdout_level = logging._checkLevel(stdout_level)  # type: ignore
        self.stderr_level = logging._checkLevel(stderr_level)  # type: ignore

        # We use a list to make this context manager re-entrant.
        self._old_stdouts: typing.List[typing.TextIO] = []
        self._old_stderrs: typing.List[typing.TextIO] = []

    def __enter__(self) -> logging.Logger:
        self._old_stdouts.append(sys.stdout)
        sys.stdout = typing.cast(typing.TextIO, StreamToLogger(self.logger, self.stdout_level))
        self._old_stderrs.append(sys.stderr)
        sys.stderr = typing.cast(typing.TextIO, StreamToLogger(self.logger, self.stderr_level))
        return self.logger

    def __exit__(self, exc_type: typing.Optional[typing.Type[BaseException]],
                 exc_value: typing.Optional[BaseException],
                 traceback: typing.Optional[types.TracebackType]) -> typing.Optional[bool]:
        sys.stdout = self._old_stdouts.pop()
        sys.stderr = self._old_stderrs.pop()
        return None


def get_full_name(value: typing.Any) -> str:
    return '{module}.{name}'.format(module=value.__module__, name=value.__name__)


def has_duplicates(data: typing.Sequence) -> bool:
    """
    Returns ``True`` if ``data`` has duplicate elements.

    It works both with hashable and not-hashable elements.
    """

    try:
        return len(set(data)) != len(data)
    except TypeError:
        n = len(data)
        for i in range(n):
            for j in range(i + 1, n):
                if data[i] == data[j]:
                    return True
        return False


@contextlib.contextmanager
def silence() -> typing.Generator:
    """
    Hides logging and stdout output.
    """

    with unittest.TestCase().assertLogs(level=logging.DEBUG):
        with redirect_to_logging():
            # Just to log something, otherwise "assertLogs" can fail.
            logging.getLogger().debug("Silence.")

            yield


def columns_sum(inputs: typing.Any, *, source: typing.Any = None) -> typing.Any:
    """
    Computes sum per column.
    """

    # Importing here to prevent import cycle.
    from d3m import container

    if isinstance(inputs, container.DataFrame):  # type: ignore
        results = container.DataFrame(inputs.agg(['sum']).reset_index(drop=True), generate_metadata=False, source=source)  # type: ignore
        results.metadata = inputs.metadata.set_for_value(results, generate_metadata=True, source=source)
        return results

    elif isinstance(inputs, container.ndarray) and len(inputs.shape) == 2:
        return numpy.sum(inputs, axis=0, keepdims=True)

    else:
        raise exceptions.InvalidArgumentTypeError("Unsupported container type to sum: {type}".format(
            type=type(inputs),
        ))


def list_files(base_directory: str) -> typing.Sequence[str]:
    files = []

    for dirpath, dirnames, filenames in os.walk(base_directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)

            if not os.path.isfile(filepath):
                continue

            files.append(os.path.relpath(filepath, start=base_directory))

    # We sort to have a canonical order.
    files = sorted(files)

    return files

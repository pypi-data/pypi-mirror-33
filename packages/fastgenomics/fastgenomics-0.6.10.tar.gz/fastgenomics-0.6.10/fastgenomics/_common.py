"""
FASTGenomics common IO helpers: Wraps manifest.json, input_file_mapping.json and parameters.json given by the
FASTGenomics runtime.

If you want to work without docker, you can set two environment variables to ease testing:

``APP_ROOT_DIR``: This path should contain manifest.json, normally this is /app.
``DATA_ROOT_DIR``: This path should contain you test data - normally, this is /fastgenomics.

You can set them by environment variables or just call ``fastgenomics.common.set_paths(path_to_app, path_to_data_root)``
"""
import os
import json
import typing as ty
from pathlib import Path
from logging import getLogger

import jsonschema

from ._resources import resource_bytes


logger = getLogger('fastgenomics.common')

# set default paths
DEFAULT_APP_DIR = '/app'
DEFAULT_DATA_ROOT = '/fastgenomics'

# init cache
_PATHS = {}
_MANIFEST = {}
_INPUT_FILE_MAPPING = {}


ParameterValue = ty.Union[dict, list, bool, int, float, str, None]
Parameters = ty.Dict[str, ParameterValue]
PathsDict = ty.Dict[str, Path]
FileMapping = ty.Dict[str, Path]


class Parameter(ty.NamedTuple):
    """Parameter entry"""
    name: str
    type: str
    value: ty.Any  # uses default for initialization or None
    default: ty.Any
    optional: bool
    enum: ty.Optional[ty.List[ty.Any]]
    description: str


def check_paths(paths: PathsDict, raise_error: bool = True):
    """
    checks, if main paths are existing along with the manifest.json and input_file_mapping.json
    """
    # check base paths
    for dir_to_check in ['app', 'config', 'data']:
        path_entry = paths.get(dir_to_check)
        if path_entry is None or not path_entry.exists():
            err_msg = f"Path to {path_entry} not found! Check paths!"
            if raise_error is True:
                raise FileNotFoundError(err_msg)
            else:
                logger.warning(err_msg)

    # check configs files
    paths_to_check = [paths['app'] / 'manifest.json']
    if not os.environ.get('INPUT_FILE_MAPPING'):
        paths_to_check.append(paths['config'] / 'input_file_mapping.json')

    for path_entry in paths_to_check:
        if not path_entry.exists():
            err_msg = f"`{path_entry}` does not exist! Please check paths and existence!"
            if raise_error is True:
                raise FileNotFoundError(err_msg)
            else:
                logger.warning(err_msg)


def check_input_file_mapping(input_file_mapping: FileMapping):
    """checks the keys in input_file_mapping and existence of the files

    raises a KeyError on missing Key and FileNotFoundError on missing file
    """
    manifest = get_app_manifest()['Input']

    not_in_manifest = set(input_file_mapping.keys()) - set(manifest.keys())
    not_in_ifm = set(manifest.keys()) - set(input_file_mapping.keys())

    optional = set([entry for entry, settings in manifest.items() if settings.get('Optional', False) is True])
    missing = not_in_ifm - optional

    # check keys
    if not_in_manifest:
        logger.warning(f"Ignoring Keys defined in input_file_mapping: {not_in_manifest}")

    if missing:
        raise KeyError(f"Non-optional keys not defined in input_file_mapping: {missing}")

    # check for existence
    for key, entry in input_file_mapping.items():
        if not entry.exists():
            if key in optional:
                logger.info(f"Optional file {entry} is not present and may cause an error - be aware!")
            else:
                raise FileNotFoundError(f"{entry}, defined in input_file_mapping, not found!")


def str_to_path_file_mapping(relative_mapping: ty.Dict[str, str]) -> FileMapping:
    """maps the relative string paths given in input_file_mapping to absolute paths"""
    data_path = get_paths()['data']

    absolute_mapping = {}
    for key, maybe_rel_path in relative_mapping.items():
        expanded = Path(os.path.expandvars(maybe_rel_path))
        if expanded.is_absolute():
            absolute_mapping[key] = expanded
        else:
            absolute_mapping[key] = data_path / expanded

    return absolute_mapping


def load_input_file_mapping() -> ty.Dict[str, str]:
    """helper function loading the input_file_mapping either from environment or from file"""
    # try to get input file mapping from environment
    empty_str = '{}'
    ifm_str = os.environ.get('INPUT_FILE_MAPPING', empty_str)
    source_str = "`INPUT_FILE_MAPPING` environment"

    # else use input_file_mapping file
    if ifm_str == empty_str:
        ifm_path = get_paths()['config'] / 'input_file_mapping.json'
        if not ifm_path.exists():
            raise FileNotFoundError(f"Input file mapping {ifm_path} not found!")

        with open(get_paths()['config'] / 'input_file_mapping.json', encoding='utf-8') as f:
            ifm_str = f.read()
            source_str = ifm_path.name
    logger.info(f"Input file mapping loaded from {source_str}.")

    # decode json:
    try:
        ifm_dict = json.loads(ifm_str)
    except json.JSONDecodeError as e:
        e.msg = f"{source_str} is not valid JSON: {e.msg}"
        raise e
    return ifm_dict


def get_input_file_mapping(check_mapping: bool = True) -> FileMapping:
    """returns the input_file_mapping either from environment `INPUT_FILE_MAPPING` or from config file"""
    global _INPUT_FILE_MAPPING

    if _INPUT_FILE_MAPPING:
        return _INPUT_FILE_MAPPING

    # load mapping
    ifm_dict = load_input_file_mapping()

    # convert into paths
    input_file_mapping = str_to_path_file_mapping(ifm_dict)

    # check existence
    if check_mapping:
        check_input_file_mapping(input_file_mapping)

    # update cache and return
    _INPUT_FILE_MAPPING = input_file_mapping
    return _INPUT_FILE_MAPPING


def get_paths() -> PathsDict:
    """
    safe getter for the runtime paths

    if paths are not initialized, it runs ``set_paths(DEFAULT_APP_DIR, DEFAULT_DATA_ROOT)``
    """
    if not _PATHS:
        from . import io
        io.set_paths()
    return _PATHS


def assert_manifest_is_valid(config: dict):
    """
    Asserts that the manifest (``manifest.json``) matches our JSON-Schema.
    If not a :py:exc:`jsonschema.ValidationError` will be raised.
    """
    
    schema = json.loads(resource_bytes('schemes/manifest_schema.json'))
    jsonschema.validate(config, schema)

    parameters = config["FASTGenomicsApplication"]["Parameters"]
    if parameters is not None:
        for name, properties in parameters.items():
            expected_type = properties["Type"]
            enum = properties.get("Enum")
            default_value = properties["Default"]
            optional = properties.get("Optional", False)
            warn_if_not_of_type(name, expected_type, enum, default_value, optional, is_default=True)


def get_app_manifest() -> dict:
    """
    Parses and returns the app manifest.json

    Raises:
        RuntimeError: If ``manifest.json`` does not exist.
    """
    global _MANIFEST

    # use cache
    if _MANIFEST:
        return _MANIFEST

    manifest_file = get_paths()['app'] / 'manifest.json'
    if not manifest_file.exists():
        err_msg = (f"App manifest {manifest_file} not found! "
                   "Please provide a manifest.json in the application's root-directory.")
        raise RuntimeError(err_msg)
    try:
        config = json.loads(manifest_file.read_bytes())
        assert_manifest_is_valid(config)
        # update cache
        _MANIFEST = config['FASTGenomicsApplication']
    except json.JSONDecodeError:
        err_msg = f"App manifest {manifest_file} not a valid JSON-file - check syntax!"
        raise RuntimeError(err_msg)

    return _MANIFEST


def _update_param_value(param: Parameter, new_value: ty.Any):
    """helper function for updating the value of a Parameter instance"""
    return Parameter(name=param.name,
                     type=param.type,
                     value=new_value,
                     default=param.default,
                     optional=param.optional,
                     enum=param.enum,
                     description=param.description)


def load_runtime_parameters() -> Parameters:
    """loads and returns the runtime parameters from parameters.json"""

    parameters_file = get_paths()['config'] / 'parameters.json'

    if not parameters_file.exists():
        logger.info(f"No runtime parameters {parameters_file} found - using defaults.")
        return {}

    try:
        runtime_parameters = json.loads(parameters_file.read_bytes())
    except json.JSONDecodeError:
        logger.error(
            f"Could not read {parameters_file} due to an unexpected error. "
            f"Please report this at https://github.com/FASTGenomics/fastgenomics-py/issues")
        return {}

    return runtime_parameters


def load_parameters_from_manifest() -> ty.Dict[str, Parameter]:
    """returns the parameters section defined in the manifest.json as dict of Parameter
    """
    param_section = get_app_manifest()['Parameters']

    return {name: Parameter(name=name,
                            type=value['Type'],
                            value=value.get('Default'),
                            default=value.get('Default'),
                            optional=value.get('Optional', False),
                            enum=value.get('Enum'),
                            description=value['Description'])

            for name, value in param_section.items()}


def value_is_of_type(expected_type: str, enum: ty.Optional[list], value: ty.Any, optional: bool) -> bool:
    """tests, of a value is an instance of a given an expected type"""
    type_mapping = {
        'float': (int, float),
        'integer': int,
        'bool': bool,
        'list': list,
        'dict': dict,
        'string': str,
        'enum': object,
    }
    mapped_type = type_mapping.get(expected_type)
    if mapped_type is None:
        raise ValueError(f"Unknown type to check: {expected_type}")

    if optional and value is None:
        return True
    if enum is not None:
        if expected_type != 'enum':
            raise ValueError(f"Enum provided but type is {expected_type}")
        return value in enum
    return isinstance(value, mapped_type)


def check_parameter_types(parameters: Parameters):
    """checks the correct type of parameters as specified in the manifest.json"""
    manifest_parameters = load_parameters_from_manifest()

    for param_name, param in parameters.items():
        manifest_param = manifest_parameters[param_name]
        # parameter types see manifest_schema.json
        # we do not throw an exception because having multi-value parameters is
        #  common in some libraries, e.g. specify "red" or 24342
        warn_if_not_of_type(name=param_name, expected_type=manifest_param.type, enum=manifest_param.enum,
                            value=param.value, optional=manifest_param.optional)


def warn_if_not_of_type(name, expected_type, enum, value, optional, is_default=False):
    if value_is_of_type(expected_type, enum, value, optional):
        return

    msg = f"The {'default ' if is_default else ''}parameter {name} has a different value than expected. "
    if enum is None:
        msg += f"It should be a {expected_type} but is a {type(value)}. "
    else:
        msg += f"It should be one of {enum!r} but is {value!r}. "
    logger.warning(msg + f"The value is accessible but beware!")

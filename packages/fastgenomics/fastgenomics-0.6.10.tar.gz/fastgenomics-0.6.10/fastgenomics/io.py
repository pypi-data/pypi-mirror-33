"""
FASTGenomics IO helpers
=======================

Wraps input/output of ``input_file_mapping.json`` and parameters given by the FASTGenomics runtime.

If you want to work without docker, you can set two environment variables to ease testing:

``APP_ROOT_DIR``: This path should contain manifest.json, normally this is /app.
``DATA_ROOT_DIR``: This path should contain you test data - normally, this is /fastgenomics.

You can set them by environment variables or just call ``fg_io.set_paths(path_to_app, path_to_data_root)``
"""
import os
import typing as ty
from pathlib import Path
from logging import getLogger

from . import _common, tools


logger = getLogger('fastgenomics.io')


_PARAMETERS = {}


class UnknownAppTypeError(Exception):
    """
    Exception for unsupported App types.

    Args:
        typ: FASTGenomics App type
    """
    def __init__(self, typ: str):
        self.typ = typ

    @classmethod
    def check_type(cls, typ: str):
        if typ != 'Calculation':
            raise cls(typ)

    @property
    def message(self):
        return f'File output for “{self.typ}” applications not supported!'

    def __str__(self):
        return f'Not Supported: {self.message}'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.typ!r})'


def set_paths(
    app_dir: ty.Optional[str] = None,
    data_root: ty.Optional[str] = None,
):
    """
    Sets the paths for the module to search for the ``manifest.json`` and IO/files

    The following strategy is used:

    - use variables provided to function, but warn if running within docker
    - else: if set, use environment-variables ``FG_APP_DIR`` and ``FG_DATA_ROOT``
    - else: if running within docker use defaults ``/app`` and ``/fastgenomics``
    - else: raise exception

    Args:
        app_dir: Path to root directory of the application (must contain ``manifest.json``)
        data_root: Path to root directory of input/output/config/summary
    
    Raises:
        FileNotFoundError: If any mapped paths do not point to files.
    """
    if tools.running_within_docker() is True:
        if any([app_dir, data_root, os.environ.get("FG_APP_DIR"), os.environ.get("FG_DATA_ROOT")]):
            logger.warning("Running within docker - non-default paths may result in errors!")

    if app_dir is None:
        app_dir_path = Path(os.environ.get("FG_APP_DIR", _common.DEFAULT_APP_DIR)).absolute()
    else:
        app_dir_path = Path(app_dir).absolute()

    if data_root is None:
        data_root_path = Path(os.path.expandvars(os.environ.get("FG_DATA_ROOT", _common.DEFAULT_DATA_ROOT))).absolute()
    else:
        data_root_path = Path(data_root).absolute()

    logger.info(f"Using {app_dir_path} as app directory")
    logger.info(f"Using {data_root_path} as data root")

    # set paths
    paths = dict(
        app=app_dir_path,
        data=data_root_path / Path('data'),
        config=data_root_path / Path('config'),
        output=data_root_path / Path('output'),
        summary=data_root_path / Path('summary'),
    )

    _common.check_paths(paths)

    # Invalidate parameter cache when changing paths
    if _common._PATHS != paths:
        _PARAMETERS.clear()
        _common._INPUT_FILE_MAPPING.clear()
        _common._MANIFEST.clear()
        _common._PATHS = paths


def get_input_path(input_key: str) -> ty.Optional[Path]:
    """
    Retrieves the location of a input file.
    Keep in mind that you have to define your input files in your ``manifest.json`` in advance!

    Args:
        input_key: Key of an input file

    Returns:
        Location of the input file or None if the file is optional and not specified in the input file mapping.

    Raises:
        KeyError: If the ``input_key`` is not defined in ``manifest.json``
        FileNotFoundError: If the mapped path does not point to a file
    """
    manifest = _common.get_app_manifest()['Input']
    input_file_mapping = _common.get_input_file_mapping()

    # check for key in manifest
    if input_key not in manifest:
        err_msg = f"Input '{input_key}' not defined in manifest.json!"
        logger.error(err_msg)
        raise KeyError(err_msg)

    if manifest[input_key].get('Optional', False):
        input_file = input_file_mapping.get(input_key)
    else:
        # check for key in mapping
        if input_key not in input_file_mapping:
            err_msg = f"Input '{input_key}' not defined in input_file_mapping!"
            logger.error(err_msg)
            raise KeyError(err_msg)
        input_file = input_file_mapping[input_key]

    # check existence
    if not (input_file is None or input_file.exists()):
        err_msg = f"Input-file '{input_file}' not found! Please check your input_file_mapping."
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    return input_file


def get_output_path(output_key: str) -> Path:
    """
    Retrieves the location of the output file.
    Keep in mind that you have to define your output files in your ``manifest.json`` in advance!

    You can use this path-object to write your output as follows::

        my_path_object = get_output_path('my_output_key')
        with my_path_object.open('w', encoding='utf-8') as f_out:
            f_out.write("something")

    Args:
        output_key: Key of an output file

    Returns:
        Location of the output file
    
    Raises:
        UnknownAppTypeError: If the app type is unknown
        KeyError: If the ``output_key`` is not defined
    """
    manifest = _common.get_app_manifest()

    UnknownAppTypeError.check_type(manifest['Type'])

    # get output_file_mapping
    output_file_mapping = manifest['Output']
    if output_key not in output_file_mapping:
        err_msg = f"Key '{output_key}' not defined in manifest.json!"
        logger.error(err_msg)
        raise KeyError(err_msg)

    output_file = _common.get_paths()['output'] / output_file_mapping[output_key]['FileName']

    # check for existence
    if output_file.exists():
        err_msg = f"Output-file '{output_file}' already exists!"
        logger.warning(err_msg)

    return output_file


def get_summary_path() -> Path:
    """
    Retrieves the location of the summary file.
    Please write your summary as CommonMark-compatible Markdown into this file.

    Returns:
        Location of the summary file
    
    Raises:
        UnknownAppTypeError: If the app type is unknown
    """
    manifest = _common.get_app_manifest()

    UnknownAppTypeError.check_type(manifest['Type'])

    output_file = _common.get_paths()['summary'] / 'summary.md'

    # check for existence
    if output_file.exists():
        err_msg = f"Summary-file '{output_file}' already exists!"
        logger.warning(err_msg)

    return output_file


def get_parameters() -> _common.Parameters:
    """
    Returns a dict of all parameters along with its current value provided by
    ``parameters.json``, falling back to defaults defined in ``manifest.json``.

    Unset optional Parameters result in ``None`` values.

    Returns:
        Parameter dict with current values
    """
    global _PARAMETERS

    # use cache and return dict of {param: current value}
    if _PARAMETERS:
        return _return_parameters()

    # else: load parameters
    parameters = _common.load_parameters_from_manifest()
    runtime_parameters = _common.load_runtime_parameters()

    # merge with defaults
    for name, current_value in runtime_parameters.items():
        if name not in parameters:
            logger.warning(f"Ignoring runtime parameter {name}, as it is not defined in manifest.json!")
            continue
        parameters[name] = _update_param_value(parameters[name], current_value)

    # check types
    _common.check_parameter_types(parameters)

    # update cache and return
    _PARAMETERS = parameters
    return _return_parameters()


def _return_parameters() -> _common.Parameters:
    """helper for structured return of parameters"""
    return {name: param.value for name, param in _PARAMETERS.items()}


def _update_param_value(param: _common.Parameter, new_value: ty.Any):
    """helper function for updating the value of a Parameter instance"""
    return _common.Parameter(
        name=param.name,
        type=param.type,
        value=new_value,
        default=param.default,
        optional=param.optional,
        enum=param.enum,
        description=param.description,
    )


def get_parameter(param_key: str) -> _common.ParameterValue:
    """
    Get a specific parameter's current value or the default.
    Provide a key defined in the ``manifest.json``.
    
    Unset optional Parameters result in ``None`` being returned.
    
    Args:
        param_key: The parameter's key
    
    Returns:
        The parameter's value.
    
    Raises:
        KeyError: If a parameter named ``param_key`` is not defined
    """
    parameters = get_parameters()

    # check for existence and return or raise exception
    if param_key not in parameters:
        raise KeyError(f"Parameter {param_key} not defined in manifest.json!")
    return parameters[param_key]

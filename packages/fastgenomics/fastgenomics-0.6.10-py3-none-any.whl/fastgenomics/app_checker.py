"""
FASTGenomics Test-Suite
=======================

Provides methods to check your app structure, ``manifest.json`` and ``input_file_mapping.json``.
"""
from pathlib import Path
from logging import getLogger

from . import _common, io


logger = getLogger('fastgenomics.testing')


def check_app_structure(app_dir: Path):
    """
    Checks the structure of your app –
    only checks for mandatory files and directories.

    It only logs warnings if default parameter types are off.
    
    Args:
        app_dir: Root directory of the app

    Raises:
        AssertionError: If any vital files are missing
        ~jsonschema.exceptions.ValidationError: If the manifest isn’t valid
    """

    # check app structure
    logger.info(f"Checking app-structure in {app_dir}")
    to_check = ['manifest.json', 'README.md', 'LICENSE', 'Dockerfile', 'requirements.txt']
    warn_only = ['LICENSE', 'requirements.txt']

    missing = []
    for entry in to_check:
        entry_path = app_dir / entry
        if not entry_path.exists():
            err_msg = f"{entry_path} is missing!"
            if entry in warn_only:
                logger.warning(err_msg)
            else:
                logger.error(err_msg)
                missing.append(entry_path)
    assert not missing, missing

    # check manifest.json
    logger.info(f"Checking manifest.json in {app_dir}")
    manifest = _common.get_app_manifest()
    # This is already done in get_app_manifest, but let’s make sure this is tested
    _common.assert_manifest_is_valid(dict(FASTGenomicsApplication=manifest))

    # checking for sample_data
    logger.info(f"Checking for sample_data in {app_dir}")
    sample_dir = app_dir / 'sample_data'

    valid_sample_data_sub_dirs = ['data', 'config']
    if manifest['Type'] == 'Calculation':
        valid_sample_data_sub_dirs += ['output', 'summary']

    if not sample_dir.exists():
        logger.warning("No sample_data found - please provide sample data!")
    else:
        for sub_dir in valid_sample_data_sub_dirs:
            assert (sample_dir / sub_dir).exists(), f"sample_data subdirectory {sub_dir} is missing!"


def check_input_file_mapping(app_dir: Path):
    """
    Checks the input_file_mapping
    
    Args:
        app_dir: Root directory of the app

    Raises:
        FileNotFoundError: If any mapped paths do not point to files.
        ~json.JSONDecodeError: If the manifest is not valid JSON
        KeyError: If an file in the manifest is not mapped
    """
    sample_dir = app_dir / 'sample_data'
    io.set_paths(str(app_dir), str(sample_dir))
    _common.get_input_file_mapping(check_mapping=True)

"""
FASTGenomics App Creation Suite
===============================

Provides methods to create basic boilerplate for your apps.
"""
from pathlib import Path
from logging import getLogger

from ._resources import j2env
from . import _common


logger = getLogger('fastgenomics.testing')


# registry
DOCKER_REGISTRY = 'apps.fastgenomics.org'


def create_docker_compose(app_dir: Path, app_name: Path, sample_dir: Path, docker_registry: str = DOCKER_REGISTRY):
    """
    Creates an ``docker-compose.test.yml`` for testing
    
    Args:
        app_dir: Root directory of the app
        app_name: Name of the app, ``snake_case``
        sample_dir: Data root dir containing ``data/**`` and ``config/input_file_mapping.json``
        docker_registry: App registry
    """
    docker_compose_file = app_dir / 'docker-compose.test.yml'

    if docker_compose_file.exists():
        logger.warning(f"{docker_compose_file.name} already existing! Aborting.")
        return

    # get app type
    manifest = _common.get_app_manifest()
    app_type = manifest['Type']

    logger.info("Loading docker-compose.test.yml template")
    template = j2env.get_template('docker-compose.yml.j2')

    logger.info(f"Writing {docker_compose_file}")
    with docker_compose_file.open('w') as f_out:
        temp = template.render(
            app_name=app_name,
            sample_dir=sample_dir.relative_to(app_dir),
            docker_registry=docker_registry,
            app_type=app_type,
        )
        f_out.write(temp)


def create_file_mapping(sample_dir: Path):
    """
    Creates a base ``input_file_mapping.json``
    
    Args:
        sample_dir: Sample data directory that will contain ``data/**`` and ``config/input_file_mapping.json``
    """
    sample_output_dir = sample_dir / 'data' / 'other_app_uuid' / 'output'
    file_mapping_file = sample_dir / 'config' / 'input_file_mapping.json'

    if file_mapping_file.exists():
        logger.warning(f"{file_mapping_file} already existing! Aborting.")
        return

    # creating output directories
    sample_output_dir.mkdir(parents=True, exist_ok=True)
    file_mapping_file.parent.mkdir(parents=True, exist_ok=True)

    # create file_mappings
    manifest = _common.get_app_manifest()
    input_keys = manifest['Input'].keys()
    file_mapping = {key: sample_output_dir / 'fix_me.txt' for key in input_keys}

    # write file_mappings
    logger.info("Loading input_file_mapping.json template")
    template = j2env.get_template('input_file_mapping.json.j2')

    logger.info(f"Writing {file_mapping_file}")
    with file_mapping_file.open('w') as f_out:
        temp = template.render(file_mapping=file_mapping)
        f_out.write(temp)

    print()
    print(f"Please edit {file_mapping_file} and provide the following files:")
    for key in input_keys:
        print(f" - {key}: {manifest['Input'][key]['Usage']} ({manifest['Input'][key]['Type']})")
    print()

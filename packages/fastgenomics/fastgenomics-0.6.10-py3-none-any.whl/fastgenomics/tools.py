"""
FASTGenomics tools for app development
"""
from pathlib import Path
from logging import getLogger


logger = getLogger('fastgenomics.tools')


def running_within_docker() -> bool:
    """
    detects, if module is running within docker and returns the result as bool
    """
    if Path('/.dockerenv').exists():
        logger.debug("Running within docker")
        return True
    else:
        logger.info("Running locally")
        return False

from pathlib import Path
from typing import Callable

import ijson

from rpm_package import Package, PackageSet


def load_compose_json_file(
    filepath: Path, prefix: str, get_pkg: Callable
) -> PackageSet:
    """Load and parse packages from a JSON compose file.

    Args:
        filepath: Path to the JSON file containing package information
        prefix: JSON prefix to locate package data within the file
        get_pkg: Callable that converts raw package data into Package objects

    Returns:
        PackageSet containing all parsed Package objects from the file
    """
    payloads: PackageSet[Package] = PackageSet()
    with open(filepath, mode="rb") as f:
        pkgs = ijson.kvitems(f, prefix, use_float=True)
        for k, v in pkgs:
            payloads.add(get_pkg(k))

    return payloads

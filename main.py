from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from time import perf_counter
from typing import Callable

import ijson

from cli_argparse import create_argparser
from cli_output import display_pkg_changes
from rpm_package import (
    Package,
    PackageSet,
    get_added_pkgs,
    get_changed_pkgs,
    get_removed_pkgs,
    parse_nevra,
)
from web_parse import get_latest_rawhide_compose_dirs


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


def main():
    parser = create_argparser()
    args = parser.parse_args()

    if args.days_ago:
        rawhide_dirs = get_latest_rawhide_compose_dirs(args.days_ago)
        print(rawhide_dirs)
        exit()

    # Parse both JSON files in parallel and create two sets of Packages for old and new compose
    load_compose_parse_nerva = partial(load_compose_json_file, get_pkg=parse_nevra)
    with ProcessPoolExecutor() as pool:
        result = pool.map(
            load_compose_parse_nerva,
            [Path(args.old_rpm), Path(args.new_rpm)],
            [args.json_prefix, args.json_prefix],
        )
    old_pkgs, new_pkgs = result
    removed = get_removed_pkgs(old_pkgs, new_pkgs)
    added = get_added_pkgs(old_pkgs, new_pkgs)
    changed = get_changed_pkgs(removed, added)

    display_pkg_changes(
        removed=removed.difference(changed["old"]),
        added=added.difference(changed["new"]),
        changed=changed,
    )


if __name__ == "__main__":
    start = perf_counter()
    main()
    end = perf_counter()
    print(f"\nTime elapsed: {end - start:.6f}s")

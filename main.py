from concurrent.futures import ProcessPoolExecutor
from functools import partial
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


def load_compose_json_file(filepath: str, prefix: str, get_pkg: Callable) -> PackageSet:
    payloads: PackageSet[Package] = PackageSet()
    # TODO use path from Pathlib instead of str
    with open(filepath, "br") as f:
        pkgs = ijson.kvitems(f, prefix, use_float=True)
        for k, v in pkgs:
            payloads.add(get_pkg(k))

    return payloads


def main():
    parser = create_argparser()
    args = parser.parse_args()

    # Parse both JSON files in parallel and create two sets of Packages for old and new compose
    load_compose_parse_nerva = partial(load_compose_json_file, get_pkg=parse_nevra)
    with ProcessPoolExecutor() as pool:
        result = pool.map(
            load_compose_parse_nerva,
            [args.old_rpm, args.new_rpm],
            [args.json_prefix, args.json_prefix],
        )
    old_pkgs, new_pkgs = result

    removed = get_removed_pkgs(old_pkgs, new_pkgs)
    added = get_added_pkgs(old_pkgs, new_pkgs)
    changed = get_changed_pkgs(removed, added)

    # Get only packages that have been completely removed (in old but not in new)
    completely_removed = removed.difference(changed["old"])
    # Get only completely new additions (in new but not in old)
    completely_new = added.difference(changed["new"])

    # TODO output should be templated in a separate module
    print(f"REMOVED: {list(completely_removed)}")
    print(f"ADDED: {list(completely_new)}")
    print(f"CHANGED: {list(changed['old'])} -> {list(changed['new'])}")


if __name__ == "__main__":
    start = perf_counter()
    main()
    end = perf_counter()
    print(f"Time elapsed: {end - start:.6f}s")

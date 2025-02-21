import argparse
from concurrent.futures import ProcessPoolExecutor
from difflib import SequenceMatcher
from time import perf_counter
from typing import Dict, List

import ijson

PREFIX: str = "payload.rpms.Everything.x86_64"


def parse_rpm_json_file(filepath: str, prefix: str) -> set[str]:
    # TODO use path from Pathlib instead of str
    payloads = set()
    with open(filepath, "br") as f:
        pkgs = ijson.kvitems(f, prefix, use_float=True)
        for k, v in pkgs:
            payloads.add(k)

    return payloads


def get_nochanged_pkgs(old: set[str], new: set[str]) -> set[str]:
    return old.intersection(new)


def get_added_pkgs(old: set[str], new: set[str]) -> set[str]:
    return new - old


def get_removed_pkgs(old: set[str], new: set[str]) -> set[str]:
    return old - new


def get_changed_pkgs(
    removed_pkgs: set[str], added_pkgs: set[str]
) -> Dict[str, List[str]]:
    changed: Dict[str, List[str]] = {"old": [], "new": []}

    for old_item in removed_pkgs:
        for new_item in added_pkgs:
            if (
                # TODO parse and filter the %name out and compare similarity of %version only
                # %{name}-%{version}-%{release}.%{arch} do not rely on .ratio()
                # does not recognize changes like this:
                # rust-uuid-0:1.11.0-2.fc42.src -> rust-uuid-0:1.13.2-1.fc43.src
                # python-trio-websocket-0:0.12.0~dev^202501304247cd5-1.fc43.src -> python-trio-websocket-0:0.12.1-1.fc43.src
                SequenceMatcher(None, old_item, new_item).ratio()
                > 0.9
            ):
                changed["old"].append(old_item)
                changed["new"].append(new_item)
                # TODO order matters here, probably not a great idea to blindly add each side to a list
                # without checking if the item has the correct counterpart

    return changed


def main():
    parser = argparse.ArgumentParser(
        description="""Python CLI tools to parse two Fedora Rawhide composes and return lists of packages that
          have been removed, added or changed between the two versions."""
    )
    parser.add_argument(dest="old_rpm", help="Filepath to old RPM JSON file")
    parser.add_argument(dest="new_rpm", help="Filepath to new RPM JSON file")
    args = parser.parse_args()

    # Parse both JSON files and create a set of all packages for old and new version
    with ProcessPoolExecutor() as pool:
        result = pool.map(
            parse_rpm_json_file,
            # ["compose_metadata/rpms_1802.json", "compose_metadata/rpms_1902.json"],
            [args.old_rpm, args.new_rpm],
            [PREFIX, PREFIX],
        )
    old_rpms, new_rpms = result

    removed = get_removed_pkgs(old_rpms, new_rpms)
    added = get_added_pkgs(old_rpms, new_rpms)
    changed = get_changed_pkgs(removed, added)

    # Get only packages that have been completely removed
    completely_removed = [
        i for i in removed if i not in set(changed["new"]).union(changed["old"])
    ]
    # Get only completely new additions that have not existed before
    completely_new = [
        i for i in added if i not in set(changed["new"]).union(changed["old"])
    ]

    # TODO pretty output should be templated
    print(f"REMOVED: {completely_removed}")
    print(f"ADDED: {completely_new}")
    print(f"CHANGED: {changed}")


if __name__ == "__main__":
    start = perf_counter()
    main()
    end = perf_counter()
    print(f"Time elapsed: {end - start:.6f}s")

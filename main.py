import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial
from time import perf_counter
from typing import Callable, Dict, Iterator, List, MutableSet, Set, TypeVar

import ijson

# TODO change into config file
PREFIX: str = "payload.rpms.Everything.x86_64"


@dataclass
class Package:
    name: str
    full_name: str
    epoch: str
    version: str
    release: str
    distro_version: str
    arch: str

    def __str__(self) -> str:
        return self.full_name

    def __hash__(self) -> int:
        return hash(self.full_name)  # Full name should be unique

    # def __eq__(self, other: object) -> bool:
    #     if not isinstance(other, Package):
    #         return NotImplemented
    #     return self.full_name == other.full_name


T = TypeVar("T", bound=Package)


class PackageSet(MutableSet[T]):
    def __init__(self, items: Set[T] | None = None) -> None:
        self._items: Set[T] = set() if items is None else set(items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def add(self, item: T) -> None:
        self._items.add(item)

    def discard(self, item: T) -> None:
        self._items.discard(item)

    def intersection(self, other: "PackageSet[T]") -> "PackageSet[T]":
        return PackageSet(self._items.intersection(other._items))

    def difference(self, other: "PackageSet[T]") -> "PackageSet[T]":
        return PackageSet(self._items.difference(other._items))


def parse_rpm_json_file(filepath: str, prefix: str, get_pkg: Callable) -> PackageSet:
    payloads: PackageSet[Package] = PackageSet()
    # TODO use path from Pathlib instead of str
    with open(filepath, "br") as f:
        pkgs = ijson.kvitems(f, prefix, use_float=True)
        for k, v in pkgs:
            payloads.add(get_pkg(k))

    return payloads


def get_pkg(pkg: str) -> Package:
    """Parse package NEVRA string into component parts and cosntruct Package object

    Format: {name}-{epoch}:{pkg_ver}-{pkg_rls}.{distro_rls}.{arch}

    Example: rust-uuid-1:1.13.2-1.fc43.src will results into:

    Package(
        name="rust-uuid",
        full_name=rust-uuid-1:1.13.2-1.fc43.src,
        epoch="1",
        version="1.13.2",
        release="4",
        distro_version="fc43",
        arch="src",
    )
    """
    print(f"\n{pkg}")

    # Split arch first
    pkg_base, arch = pkg.rsplit(".", 1)

    # Try to split distro version if it exists otherwise set it to empty string
    parts = pkg_base.rsplit(".", 1)
    if len(parts) > 1:
        nev, distro_rls = parts
    else:
        nev = parts[0]
        distro_rls = ""

    # Split name, epoch:version, and release
    print(f"pkg_base: {pkg_base}")
    print(f"arch: {arch}")
    print(f"distro_rls: {distro_rls}")
    print(f"nev: {nev}")
    name, epoch_ver, pkg_rls = nev.rsplit("-", 2)

    print(f"name: {name}")
    print(f"epoch: {epoch_ver}")
    print(f"version: {pkg_rls}")
    # Split epoch and pkg version
    epoch, pkg_ver = epoch_ver.split(":")

    return Package(
        name=name,
        full_name=pkg,
        epoch=epoch,
        version=pkg_ver,
        release=pkg_rls,
        distro_version=distro_rls,
        arch=arch,
    )


def get_nochanged_pkgs(old: PackageSet, new: PackageSet) -> PackageSet:
    return old.intersection(new)


def get_added_pkgs(old: PackageSet, new: PackageSet) -> PackageSet:
    return new.difference(old)


def get_removed_pkgs(old: PackageSet, new: PackageSet) -> PackageSet:
    return old.difference(new)


def get_changed_pkgs(
    removed_pkgs: PackageSet, added_pkgs: PackageSet
) -> Dict[str, List[Package]]:
    changed: Dict[str, List[Package]] = {"old": [], "new": []}

    for removed in removed_pkgs:
        for added in added_pkgs:
            if (
                removed["epoch"] != added["epoch"]
                or removed["version"] != added["version"]
                or removed["release"] != added["release"]
                or removed["fedora_version"] != added["fedora_version"]
            ):
                # TODO order matters here, probably not a great idea to blindly add each side to a list
                # without checking if the item has the correct counterpart
                changed["old"].append(removed)
                changed["new"].append(added)

    return changed


def main():
    parser = argparse.ArgumentParser(
        description="""Python CLI tools to parse two Fedora Rawhide composes and return lists of packages that
          have been removed, added or changed between the two versions."""
    )
    parser.add_argument(dest="old_rpm", help="Filepath to old RPM JSON file")
    parser.add_argument(dest="new_rpm", help="Filepath to new RPM JSON file")
    parser.add_argument(
        "-p",
        "--prefix",
        dest="json_prefix",
        default=PREFIX,
        help="The ijson prefix used to specify the JSON object to parse from the files, default: payload.rpms.Everything.x86_64",
    )
    args = parser.parse_args()

    # Parse both JSON files in parallel and create two sets of Packages for old and new composes both
    parse_and_get_pkg = partial(parse_rpm_json_file, get_pkg=get_pkg)
    with ProcessPoolExecutor() as pool:
        result = pool.map(
            parse_and_get_pkg,
            [args.old_rpm, args.new_rpm],
            [args.json_prefix, args.json_prefix],
        )
    old_pkgs, new_pkgs = result

    removed = get_removed_pkgs(old_pkgs, new_pkgs)
    added = get_added_pkgs(old_pkgs, new_pkgs)
    changed = get_changed_pkgs(removed, added, get_pkg)

    # Get only packages that have been completely removed
    completely_removed = [
        i for i in removed if i not in set(changed["new"]).union(changed["old"])
    ]
    # Get only completely new additions that have not existed before
    completely_new = [
        i for i in added if i not in set(changed["new"]).union(changed["old"])
    ]

    # TODO output should be templated in a separate module
    print(f"REMOVED: {completely_removed}")
    print(f"ADDED: {completely_new}")
    print(f"CHANGED: {changed}")


if __name__ == "__main__":
    start = perf_counter()
    main()
    end = perf_counter()
    print(f"Time elapsed: {end - start:.6f}s")

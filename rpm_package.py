from dataclasses import dataclass
from typing import Dict, Iterator, MutableSet, Set, TypeVar


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
        return hash(self.full_name)  # assuming full name is unique

    def __getitem__(self, key: str) -> str:
        return getattr(self, key)


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


def parse_nevra(pkg: str) -> Package:
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
    if ".fc" in pkg:
        name_epoch, version_rls_distro_rls_arch = pkg.split(":", 1)
        version_rls, distro_rls, arch = version_rls_distro_rls_arch.rsplit(".", 2)
    else:
        # if distro_rls is not present, we set it to empty string and parse the rest accordingly
        distro_rls = ""
        name_epoch, version_rls_arch = pkg.split(":", 1)
        version_rls, arch = version_rls_arch.rsplit(".", 1)

    name, epoch = name_epoch.rsplit("-", 1)
    pkg_ver, pkg_rls = version_rls.rsplit("-", 1)

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
    old: PackageSet[Package], new: PackageSet[Package]
) -> Dict[str, PackageSet[Package]]:

    changed: Dict[str, PackageSet[Package]] = {"old": PackageSet(), "new": PackageSet()}

    old_by_name = {pkg.name: pkg for pkg in old}
    new_by_name = {pkg.name: pkg for pkg in new}

    for name, old_pkg in old_by_name.items():
        if name in new_by_name:
            new_pkg = new_by_name[name]
            if (
                old_pkg.epoch != new_pkg.epoch
                or old_pkg.version != new_pkg.version
                or old_pkg.release != new_pkg.release
                or old_pkg.distro_version != new_pkg.distro_version
            ):
                changed["old"].add(old_pkg)
                changed["new"].add(new_pkg)

    return changed

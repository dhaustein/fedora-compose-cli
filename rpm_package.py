from dataclasses import dataclass
from typing import Dict, Iterator, MutableSet, Set, TypeVar


@dataclass
class Package:
    """Represents an RPM package with its NEVRA components.

    A dataclass that holds all components of a package's NEVRA (Name, Epoch, Version,
    Release, Architecture) along with distribution version information.

    Attributes:
        name: Base name of the package
        full_name: Complete package name including all NEVRA components
        epoch: Package epoch number
        version: Package version
        release: Package release number
        distro_version: Distribution version (e.g., 'fc42' for Fedora 42)
        arch: Package architecture (e.g., 'src')
    """

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
    """A mutable set collection specifically designed for Package objects.

    Implements the MutableSet interface to provide a specialized container
    for managing collections of Package objects with set operations.

    Attributes:
        _items: Internal set storing the Package objects

    Type Parameters:
        T: Type variable bound to the Package class
    """

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
    """Parse package NEVRA string into component parts and construct Package object.

    NEVRA stands for Name, Epoch, Version, Release, Architecture. This function handles
    both Fedora-style packages (with distro release) and standard packages.

    Args:
        pkg: Package string in NEVRA format
            Format: {name}-{epoch}:{pkg_ver}-{pkg_rls}.{distro_rls}.{arch}

    Returns:
        Package object with parsed components

    Example:
        >>> parse_nevra("rust-uuid-1:1.13.2-1.fc43.src")
        Package(
            name="rust-uuid",
            full_name="rust-uuid-1:1.13.2-1.fc43.src",
            epoch="1",
            version="1.13.2",
            release="1",
            distro_version="fc43",
            arch="src"
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
    """Get packages that remain unchanged between old and new package sets.

    Args:
        old: Original PackageSet to compare
        new: New PackageSet to compare

    Returns:
        PackageSet containing packages that are identical in both sets
    """
    return old.intersection(new)


def get_added_pkgs(old: PackageSet, new: PackageSet) -> PackageSet:
    """Get packages that were added in the new package set.

    Args:
        old: Original PackageSet to compare
        new: New PackageSet to compare

    Returns:
        PackageSet containing packages that exist only in the new set
    """
    return new.difference(old)


def get_removed_pkgs(old: PackageSet, new: PackageSet) -> PackageSet:
    """Get packages that were removed in the new package set.

    Args:
        old: Original PackageSet to compare
        new: New PackageSet to compare

    Returns:
        PackageSet containing packages that exist only in the old set
    """
    return old.difference(new)


def get_changed_pkgs(
    old: PackageSet[Package], new: PackageSet[Package]
) -> Dict[str, PackageSet[Package]]:
    """Get packages that have changed versions between old and new package sets.

    Detects changes in epoch, version, release, or distro_version for packages
    that exist in both sets but have different versions.

    Args:
        old: Original PackageSet to compare
        new: New PackageSet to compare

    Returns:
        Dictionary with two keys:
            'old': PackageSet containing the old versions of changed packages
            'new': PackageSet containing the new versions of changed packages
    """

    changed: Dict[str, PackageSet[Package]] = {"old": PackageSet(), "new": PackageSet()}

    # align old and new package sets on the name of the package
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

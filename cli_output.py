from typing import Dict, List

from rich.console import Console
from rich.text import Text

from rpm_package import Package, PackageSet

console = Console()


def display_pkg_changes(
    removed: PackageSet[Package],
    added: PackageSet[Package],
    changed: Dict[str, PackageSet[Package]],
) -> None:
    for pkg in sorted(removed, key=lambda x: x.name):
        text = Text()
        text.append(pkg.name)
        text.append(f" ADDED ({pkg.name}-{pkg.epoch}:{pkg.version}-{pkg.release})")
        console.print(text, style="red")

    for pkg in sorted(added, key=lambda x: x.name):
        text = Text()
        text.append(pkg.name)
        text.append(f" REMOVED ({pkg.name}-{pkg.epoch}:{pkg.version}-{pkg.release})")
        console.print(text, style="green")

    # sort on name to align both sets of old/new packages
    old_pkgs = sorted(changed["old"], key=lambda x: x.name)
    new_pkgs = sorted(changed["new"], key=lambda x: x.name)
    for old_pkg, new_pkg in zip(old_pkgs, new_pkgs):
        text = Text()
        text.append(old_pkg.name)
        text.append(
            f" CHANGED ({old_pkg.version}-{old_pkg.release} -> {new_pkg.version}-{new_pkg.release})"
        )
        console.print(text, style="yellow")


def display_latest_dirs(dirs: List[tuple[str, str, int]]) -> None:
    for dir_name in dirs:
        name, timestamp, generation = dir_name
        text = Text()
        text.append(name, style="green")
        text.append(f"_{timestamp}_", style="cyan")
        text.append(str(generation))
        console.print(text)

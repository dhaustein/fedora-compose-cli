from rich.console import Console
from rich.text import Text

from rpm_package import Package, PackageSet

console = Console()


def display_pkg_changes(
    removed: PackageSet[Package],
    added: PackageSet[Package],
    changed: PackageSet[Package],
) -> None:
    for pkg in removed:
        text = Text()
        text.append(pkg.name)
        text.append(f" ADDED ({pkg.name}-{pkg.epoch}:{pkg.version}-{pkg.release})")
        console.print(text, style="red")

    for pkg in added:
        text = Text()
        text.append(pkg.name)
        text.append(f" REMOVED ({pkg.name}-{pkg.epoch}:{pkg.version}-{pkg.release})")
        console.print(text, style="green")

    old_pkgs = sorted(changed["old"], key=lambda x: x.name)
    new_pkgs = sorted(changed["new"], key=lambda x: x.name)
    for pkg in zip(old_pkgs, new_pkgs):  # FIXME
        text = Text()
        text.append(pkg[0].name)
        text.append(f" CHANGED ({pkg[0].version} -> {pkg[1].version})")
        console.print(text, style="yellow")

import pytest  # noqa: F401

from json_parse import load_compose_json_file
from rpm_package import (
    Package,
    PackageSet,
    get_added_pkgs,
    get_changed_pkgs,
    get_removed_pkgs,
    parse_nevra,
)


def test_parse_dev_pkg():
    pkg_name = "python-trio-websocket-0:0.12.0~dev^202501304247cd5-1.fc43.src"
    expected_pkg = Package(
        name="python-trio-websocket",
        full_name=pkg_name,
        epoch="0",
        version="0.12.0~dev^202501304247cd5",
        release="1",
        distro_version="fc43",
        arch="src",
    )
    assert parse_nevra(pkg_name) == expected_pkg


def test_parse_pkg():
    pkg_name = "rust-uuid-1:1.13.2-4.fc43.src"
    expected_pkg = Package(
        name="rust-uuid",
        full_name=pkg_name,
        epoch="1",
        version="1.13.2",
        release="4",
        distro_version="fc43",
        arch="src",
    )
    assert parse_nevra(pkg_name) == expected_pkg


def test_parse_dummy_test_pkg():
    pkg_name = "dummy-test-package-crested-0:0-3771.src"
    expected_pkg = Package(
        name="dummy-test-package-crested",
        full_name=pkg_name,
        epoch="0",
        version="0",
        release="3771",
        distro_version="",  # no distro version for this pkg
        arch="src",
    )
    assert parse_nevra(pkg_name) == expected_pkg


def test_parse_shim_pkg():
    pkg_name = "shim-0:15.8-3.src"
    expected_pkg = Package(
        name="shim",
        full_name=pkg_name,
        epoch="0",
        version="15.8",
        release="3",
        distro_version="",  # no distro version for this pkg
        arch="src",
    )
    assert parse_nevra(pkg_name) == expected_pkg


def test_parse_nevra_with_dots_in_name():
    pkg_name = "perl-Math.Complex-0:1.59-1.fc43.src"
    expected_pkg = Package(
        name="perl-Math.Complex",
        full_name=pkg_name,
        epoch="0",
        version="1.59",
        release="1",
        distro_version="fc43",
        arch="src",
    )
    assert parse_nevra(pkg_name) == expected_pkg


def test_load_compose_json_empty_file():
    with pytest.raises(FileNotFoundError):
        load_compose_json_file("nonexistent.json", "prefix", lambda x: x)


def test_package_equality():
    pkg1 = Package(
        name="test",
        full_name="test-1:1.0-1.fc43.src",
        epoch="1",
        version="1.0",
        release="1",
        distro_version="fc43",
        arch="src",
    )
    pkg2 = Package(
        name="test",
        full_name="test-1:1.0-1.fc43.src",
        epoch="1",
        version="1.0",
        release="1",
        distro_version="fc43",
        arch="src",
    )
    assert pkg1 == pkg2


def test_parse_nevra_with_high_epoch():
    pkg_name = "high-epoch-pkg-99999:1.0-1.fc43.src"
    expected_pkg = Package(
        name="high-epoch-pkg",
        full_name=pkg_name,
        epoch="99999",
        version="1.0",
        release="1",
        distro_version="fc43",
        arch="src",
    )
    assert parse_nevra(pkg_name) == expected_pkg


def test_package_str_representation():
    pkg = Package(
        name="test",
        full_name="test-1:1.0-1.fc43.src",
        epoch="1",
        version="1.0",
        release="1",
        distro_version="fc43",
        arch="src",
    )
    assert str(pkg) == "test-1:1.0-1.fc43.src"


def test_package_getitem_access():
    pkg = Package(
        name="test",
        full_name="test-1:1.0-1.fc43.src",
        epoch="1",
        version="1.0",
        release="1",
        distro_version="fc43",
        arch="src",
    )
    assert pkg["name"] == "test"
    assert pkg["epoch"] == "1"
    assert pkg["version"] == "1.0"


def test_get_changed_pkgs_empty_sets():
    old_pkgs = PackageSet()
    new_pkgs = PackageSet()
    expected = {"old": PackageSet(), "new": PackageSet()}
    assert get_changed_pkgs(old_pkgs, new_pkgs) == expected


def test_get_changed_pkgs_version_update():
    old_pkg = parse_nevra("test-pkg-0:1.0-1.fc43.src")
    new_pkg = parse_nevra("test-pkg-0:2.0-1.fc43.src")
    old_pkgs = PackageSet([old_pkg])
    new_pkgs = PackageSet([new_pkg])
    result = get_changed_pkgs(old_pkgs, new_pkgs)

    assert len(result["old"]) == 1
    assert len(result["new"]) == 1
    assert result["old"].pop().version == "1.0"
    assert result["new"].pop().version == "2.0"


def test_get_changed_pkgs_multiple_changes():
    old_pkgs = PackageSet(
        [
            parse_nevra("pkg1-0:1.0-1.fc43.src"),
            parse_nevra("pkg2-0:1.0-1.fc43.src"),
            parse_nevra("pkg3-0:1.0-1.fc43.src"),
        ]
    )
    new_pkgs = PackageSet(
        [
            parse_nevra("pkg1-0:2.0-1.fc43.src"),
            parse_nevra("pkg2-0:1.0-2.fc43.src"),
            parse_nevra("pkg3-1:1.0-1.fc43.src"),
        ]
    )
    result = get_changed_pkgs(old_pkgs, new_pkgs)

    # Verify each specific change
    old_versions = {pkg.name: pkg for pkg in result["old"]}
    new_versions = {pkg.name: pkg for pkg in result["new"]}
    assert old_versions["pkg1"].version == "1.0"
    assert new_versions["pkg1"].version == "2.0"
    assert old_versions["pkg2"].release == "1"
    assert new_versions["pkg2"].release == "2"
    assert old_versions["pkg3"].epoch == "0"
    assert new_versions["pkg3"].epoch == "1"


def test_get_changed_pkgs_removed_package():
    old_pkgs = PackageSet(
        [parse_nevra("pkg1-0:1.0-1.fc43.src"), parse_nevra("pkg2-0:1.0-1.fc43.src")]
    )
    new_pkgs = PackageSet([parse_nevra("pkg1-0:1.0-1.fc43.src")])

    removed = get_removed_pkgs(old_pkgs, new_pkgs)
    assert len(removed) == 1
    removed_pkg = removed.pop()
    assert removed_pkg.name == "pkg2"
    assert removed_pkg.version == "1.0"


def test_get_changed_pkgs_added_package():
    old_pkgs = PackageSet([parse_nevra("pkg1-0:1.0-1.fc43.src")])
    new_pkgs = PackageSet(
        [parse_nevra("pkg1-0:1.0-1.fc43.src"), parse_nevra("pkg2-0:2.0-1.fc43.src")]
    )

    added = get_added_pkgs(old_pkgs, new_pkgs)
    assert len(added) == 1
    added_pkg = added.pop()
    assert added_pkg.name == "pkg2"
    assert added_pkg.version == "2.0"

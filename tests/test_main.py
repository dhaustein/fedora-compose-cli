import pytest

from main import Package, get_pkg


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
    assert get_pkg(pkg_name) == expected_pkg


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
    assert get_pkg(pkg_name) == expected_pkg


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
    assert get_pkg(pkg_name) == expected_pkg


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
    assert get_pkg(pkg_name) == expected_pkg

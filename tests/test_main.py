import pytest

from main import parse_pkg_nevra


def test_parse_dev_pkg():
    pkg_name = "python-trio-websocket-0:0.12.0~dev^202501304247cd5-1.fc43.src"
    assert parse_pkg_nevra(pkg_name) == {
        "name": "python-trio-websocket",
        "epoch": "0",
        "version": "0.12.0~dev^202501304247cd5",
        "release": "1",
        "fedora_version": "fc43",
        "arch": "src",
    }


def test_parse_pkg():
    pkg_name = "rust-uuid-1:1.13.2-1.fc43.src"
    assert parse_pkg_nevra(pkg_name) == {
        "name": "rust-uuid",
        "epoch": "1",
        "version": "1.13.2",
        "release": "1",
        "fedora_version": "fc43",
        "arch": "src",
    }

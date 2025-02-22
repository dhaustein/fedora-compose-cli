# fedora-compose-cli

A CLI tool that analyzes and compares Fedora Rawhide composes to identify package changes in the (by default) `Everything` repository section for `x86_64` architecture.

The tool helps to track:

- New packages added between the two composes
- Packages removed between the two composes
- Package version changes between the two composes

The tool can process JSON compose files and output changes in both human (CLI) and machine readable (JSON) formats.

## Usage

Run the script for two JSON composes

```bash
$ python main.py path/to/old_rpms.json path/to/new_rpms.json
```

Display help

```bash
$ python main.py --h
```

## Installation

Clone this repository.

Bootstrap the virtual environment
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Update `pip` and install `uv`
```bash
$ pip install --upgrade pip
$ pip install uv
```

Install the rest of the dependencies
```bash
$ uv sync
```

## Tests and linting

Run tests
```bash
$ pytest -v
```

Run linting
```bash
$ ruff check
```

## TODO

- feat: output a list of Rawhide composes from the last N days, maybe use `from urllib.request import urlopen`
  - requires calling and parsing the timestamps in folders at URL https://kojipkgs.fedoraproject.org/compose/rawhide/
- feat: add option to output a json file as a machine readable output format
- extra: do some performance profiling to learn where the bottlenecks are
- extra: add input validation (Pydantic?)

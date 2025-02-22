import argparse


def create_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="""Python CLI tools to parse two Fedora Rawhide composes and return lists of packages that
          have been removed, added or changed between the two versions."""
    )
    parser.add_argument(dest="old_rpm", help="Filepath to old compose JSON file")
    parser.add_argument(dest="new_rpm", help="Filepath to new compose JSON file")
    parser.add_argument(
        "-p",
        "--prefix",
        dest="json_prefix",
        default="payload.rpms.Everything.x86_64",
        help="The prefix used to specify the JSON object to parse from the files, default: payload.rpms.Everything.x86_64",
    )
    return parser

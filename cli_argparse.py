import argparse

EPILOG_TEXT = """Examples:
python main.py -o path/to/old.json -n path/to/new.json
python main.py -d 3
"""


def create_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="""Python CLI tools to parse two Fedora Rawhide composes and return lists of packages that
          have been removed, added or changed between the two versions.""",
        epilog=EPILOG_TEXT,
    )
    parser.add_argument(
        "-o",
        "--old-rpm",
        dest="old_rpm",
        type=str,
        help="Filepath to old compose JSON file",
    )
    parser.add_argument(
        "-n",
        "--new-rpm",
        dest="new_rpm",
        type=str,
        default="payload.rpms.Everything.x86_64",
        help="Filepath to new compose JSON file",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        dest="json_prefix",
        type=str,
        default="payload.rpms.Everything.x86_64",
        help="The prefix used to specify the JSON object to parse from the files, default: payload.rpms.Everything.x86_64",
    )
    parser.add_argument(
        "-d",
        "--days-ago",
        dest="days_ago",
        type=int,
        help="Number of days ago to get the latest compose dir from thew web and exits",
    )
    return parser

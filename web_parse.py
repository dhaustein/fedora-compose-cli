import urllib.request
from datetime import datetime, timedelta
from typing import List

from bs4 import BeautifulSoup
from lxml import etree

RAWHIDE_URL = "https://kojipkgs.fedoraproject.org/compose/rawhide/"
XPATH = "//a[contains(text(), 'Fedora-Rawhide')]"
DAYS_AGO = 3


def parse_dir_name(text: str) -> tuple[str, str, int]:
    """Parse the compose dir str into components

    Fedora-Rawhide-20250208.n.1/ -> Fedora-Rawhide, 20250208, 1
    Fedora-Rawhide-20250222.n.0/ -> Fedora-Rawhide, 20250222, 0
    """
    text = text.rstrip("/")
    if "latest" in text:
        return "Fedora-Rawhide", "latest", 0

    # Get name
    name, timestamp_generation = text.rsplit("-", 1)
    # Get timestamp and generation
    timestamp, _, generation = timestamp_generation.split(".")

    return (
        name,  # Fedora-Rawhide
        timestamp,  # 20250208
        int(generation),  # 0, 1, 3...
    )


def filter_dirs_by_days_ago(
    compose_dirs: List[tuple[str, str, int]], days_ago: int
) -> List[tuple[str, str, int]]:
    """Filter dirs by N days ago"""
    cutoff_date = datetime.now() - timedelta(days=days_ago)
    latest_only = []

    for compose_dir in compose_dirs:
        name, timestamp, generation = compose_dir
        if timestamp == "latest":
            latest_only.append(compose_dir)
            continue
        if datetime.strptime(timestamp, "%Y%m%d") < cutoff_date:
            latest_only.append(compose_dir)

    return latest_only


def get_latest_rawhide_compose_dirs(
    days_ago: int = DAYS_AGO,
) -> List[tuple[str, str, int]]:
    """Get the latest N days of Fedora Rawhide compose dirs from the web"""
    with urllib.request.urlopen(RAWHIDE_URL) as response:
        html = response.read()
    soup = BeautifulSoup(html, "html.parser")
    dom = etree.HTML(str(soup))

    parsed = []
    for dir_name in dom.xpath(XPATH):
        parsed.append(parse_dir_name(dir_name.text))

    return filter_dirs_by_days_ago(parsed, days_ago)

from difflib import SequenceMatcher

import ijson

PAYLOADS_RAW: dict[str, list[str]] = {"old": [], "new": []}


def main():
    # Parse both JSON files and create a set of all packages
    with open("tests/x86_old.json", "br") as f:
        arch_pkgs = ijson.kvitems(f, "payload.rpms.Everything.x86_64", use_float=True)
        for k, v in arch_pkgs:
            PAYLOADS_RAW["old"].append(k)

    with open("tests/x86_new.json", "br") as f:
        arch_pkgs = ijson.kvitems(f, "payload.rpms.Everything.x86_64", use_float=True)
        for k, v in arch_pkgs:
            PAYLOADS_RAW["new"].append(k)

    old_payload = set(PAYLOADS_RAW["old"])
    new_payload = set(PAYLOADS_RAW["new"])

    # Find exact matches (packages that did not change)
    unchanged = old_payload.intersection(new_payload)
    print("NOCHANGE:", list(unchanged))

    # Find new items
    added = new_payload - old_payload

    # Find removed items
    removed = old_payload - new_payload

    # Find changes using similarity calculation
    changed = []
    old = set()
    new = set()
    for old_item in removed:
        old.add(old_item)
        for new_item in added:
            new.add(new_item)
            if (
                # TODO parse and filter the %name out and compare similarity of %version only
                # %{name}-%{version}-%{release}.%{arch}
                SequenceMatcher(None, old_item, new_item).ratio()
                > 0.9
            ):
                changed.append(f"{old_item} -> {new_item}")

    print(f"CHANGED: {changed}")

    # Print only new additions, sans the packaged that merely changed
    new_additions = [i for i in added if i not in old]
    print(f"ADDED: {new_additions}")

    # Print only packages that have been completely removed, sans the packaged that merely changed
    removed_packages = [i for i in removed if i not in new]
    print(f"REMOVED: {removed_packages}")


if __name__ == "__main__":
    main()

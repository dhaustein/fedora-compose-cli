from difflib import SequenceMatcher
from time import perf_counter

import ijson

PAYLOADS_RAW: dict[str, list[str]] = {"old": [], "new": []}


def main():
    # Parse both JSON files and create a set of all packages
    # with open("tests/x86_old.json", "br") as f:
    with open("compose_metadata/rpms_1802.json", "br") as f:
        arch_pkgs = ijson.kvitems(f, "payload.rpms.Everything.x86_64", use_float=True)
        for k, v in arch_pkgs:
            PAYLOADS_RAW["old"].append(k)

    # with open("tests/x86_new.json", "br") as f:
    with open("compose_metadata/rpms_1902.json", "br") as f:
        arch_pkgs = ijson.kvitems(f, "payload.rpms.Everything.x86_64", use_float=True)
        for k, v in arch_pkgs:
            PAYLOADS_RAW["new"].append(k)

    old_payload = set(PAYLOADS_RAW["old"])
    new_payload = set(PAYLOADS_RAW["new"])

    # Find exact matches (packages that did not change)
    # unchanged = old_payload.intersection(new_payload)
    # print("NOCHANGE:", list(unchanged))

    # Find new items
    added = new_payload - old_payload

    # Find removed items
    removed = old_payload - new_payload

    # Find changes using similarity calculation
    all_changes = set()
    changed_out = []
    for old_item in removed:
        for new_item in added:
            if (
                # TODO parse and filter the %name out and compare similarity of %version only
                # %{name}-%{version}-%{release}.%{arch}
                # TODO not sure if ratio is good idea we need to do a complete version comparison
                SequenceMatcher(None, old_item, new_item).ratio()
                > 0.9
            ):
                # TODO bette to do this on the output side
                changed_out.append(f"{old_item} -> {new_item}")
                # keep record of all changes regardless of added or removed
                all_changes.add(new_item)
                all_changes.add(old_item)

    print(f"CHANGED: {changed_out}")

    # Print only new additions, sans the packaged that merely changed
    new_additions = [i for i in added if i not in all_changes]
    print(f"ADDED: {new_additions}")

    # Print only packages that have been completely removed, sans the packaged that merely changed
    removed_packages = [i for i in removed if i not in all_changes]
    print(f"REMOVED: {removed_packages}")


if __name__ == "__main__":
    start = perf_counter()
    main()
    end = perf_counter()
    print(f"Time elapsed: {end - start:.6f}s")

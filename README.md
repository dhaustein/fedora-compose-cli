# Notes

Format: {name}-{epoch}:{pkg_ver}-{pkg_rls}.{distro_rls}.{arch}
Example: rust-uuid-1:1.13.2-1.fc43.src ->
Package{name: rust-uuid, full_name: rust-uuid-1:1.13.2-1.fc43.src, epoch: 1, version: 1.13.2, release: 1, fedora_version: fc43, arch: src}
Package(
        name=name,
        full_name=str(pkg),
        epoch=epoch,
        version=pkg_ver,
        release=pkg_rls,
        distro_version=distro_rls,
        arch=arch,
    )

# TODO

- feat: output a list of Rawhide composes from the last N days, maybe use `from urllib.request import urlopen`
  - requires calling and parsing the folders at URL https://kojipkgs.fedoraproject.org/compose/rawhide/
- feat: add option to output a json file as a machine readable output format
- fix: add more unit tests
- feat: make human readable output pretty
  - probably needs a better way to sort and template the output (use jinja?)
  - use the Rich lib for pretty human-readable output
- extra: add a quick start and installation guides to README
- extra: do some performance profiling to learn where the bottlenecks are
- extra: add input validation (Pydantic?)

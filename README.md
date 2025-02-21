# TODO

- feat: output a list of Rawhide composes from the last N days
  - requires calling and parsing the folders at URL https://kojipkgs.fedoraproject.org/compose/rawhide/
- feat: make human readable output pretty
  - probably needs a better way to sort and template the output (use jinja?)
- feat: add option to output a json file as a machine readable output format
- fix: add more unit tests
- extra: add a quick start and installation guides to README
- extra: add python Rich lib for pretty human-readable output
- extra: do some performance profiling to learn where the bottlenecks are
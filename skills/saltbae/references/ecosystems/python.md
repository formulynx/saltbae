# Python

## pyproject.toml / setup.cfg / setup.py

### Version-bearing file

First match wins:

1. `[project].version`, when `version` is not listed in `dynamic`.
2. `[tool.poetry].version`.
3. `[tool.setuptools.dynamic].version` `attr:` / `file:` → edit the target it points to.
4. `dynamic = ["version"]` with `setuptools_scm` / `hatch-vcs` / `versioneer` in `[build-system].requires` → tag-versioned.
5. `setup.cfg`'s `[metadata].version`, literal or `attr:` / `file:`.
6. `setup.py`'s `setup(version=...)`. If not a string literal, trace it to the defining file (commonly `_version.py` / `__init__.py`) and edit that.

### Bump-rule nuance

PEP 440 pre/post/dev/local segments (`rc1`, `.post1`, `.dev0`, `+local`) are suffixes.

### Build/check

Run configured checks (e.g. `ruff`, `pytest`), then `python -m build --sdist --wheel .`. Skip if neither is configured.

### Lockfile

`uv.lock` present → `uv lock`.

# Python

## pyproject.toml / setup.cfg / setup.py

### Detection

`pyproject.toml`, `setup.cfg` or `setup.py` at the project root.

### Version-bearing file

Use the first source that applies, in this order:

1. `pyproject.toml`'s `[project].version`, as a literal key not listed under `dynamic`.
2. Else `[tool.poetry].version`.
3. Else `[tool.setuptools.dynamic].version`'s `attr:` / `file:` indirection. Edit the module attribute or file it points to, not `pyproject.toml` itself.
4. Else `dynamic = ["version"]` with `setuptools_scm` / `hatch-vcs` / `versioneer` in `[build-system].requires`. No version file exists in this case. The project is tag-versioned, and the git tag is the primary source.
5. Else `setup.cfg`'s `[metadata].version`, either a literal or its own `attr:` / `file:` indirection.
6. Else `setup.py`'s `setup(version=...)` kwarg. If the value is not a quoted string literal, trace the variable/expression to the file that defines it (commonly a `_version.py` / `__init__.py` module attribute) and treat that file as version-bearing instead.
7. Else the git-tag fallback in `SKILL.md`.

### Bump-rule nuance

PEP 440 pre/post/dev/local segments (`1.2.0rc1`, `1.2.0.post1`, `1.2.0.dev0`, `1.2.0+local`) are suffixes. Ask the user for the intended next version instead of incrementing through them.

### Build/check

- Run the configured checks if present (e.g. `ruff`, `pytest`).
- Run `python -m build --sdist --wheel .` as the build-sanity step.
- If neither checks nor a build backend is configured, skip.

### Lockfile

`uv.lock` present → run `uv lock`. It records the project's own version for the root package.

### Extra update steps

None.

# C / C++

CMake, Meson and Autotools are alternative primary build systems for the same language. If more than one is present (e.g. a project mid-migration), the consensus rule in `SKILL.md` applies. Never silently prefer one.

vcpkg and Conan are additive dependency manifests. They coexist with one of the build systems above, which remains the actual build driver. Add them to the set of files updated in sync.

## CMake

### Detection

`CMakeLists.txt` at the project root.

### Version-bearing file

`VERSION` in the top-level `project(... VERSION x.y.z ...)` call.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

`cmake --build <builddir>` if a build directory already exists from prior development. Otherwise skip. This step never bootstraps a project from scratch.

### Lockfile

None.

### Extra update steps

None.

## Meson

### Detection

`meson.build` at the project root.

### Version-bearing file

The top-level `meson.build`'s `project(...)` call's `version:` keyword argument, e.g. `project('gtk+', 'c', version: '3.94.0', ...)`.

### Bump-rule nuance

The `version:` value is a free-form string with no built-in semver enforcement. The overwhelming real-world convention is dotted `MAJOR.MINOR.PATCH`, so apply the standard numeric patch-increment rule.

### Build/check

`meson compile -C <builddir>` if a build directory already exists from prior development. Otherwise skip.

### Lockfile

None.

### Extra update steps

None.

## Autotools

### Detection

`configure.ac`, or the legacy filename `configure.in`. Both are accepted by `autoconf` / `autoreconf`. `configure.ac` is the current convention.

### Version-bearing file

`configure.ac`'s `AC_INIT([package], [x.y.z], [bug-report-address], ...)` macro call. The version is the 2nd positional argument, a bare string with no key name (e.g. `AC_INIT([amhello], [1.0], [bug-automake@gnu.org])`).

### Bump-rule nuance

The Autoconf manual leaves the string unconstrained. Real-world projects overwhelmingly use dotted numeric versions, so apply the standard numeric patch-increment rule.

### Build/check

`autoreconf`, or plain `autoconf`. These regenerate `configure` / `Makefile.in` from `configure.ac` / `Makefile.am` and catch M4/Automake syntax errors without running `./configure` or `make`.

- `autoreconf --dry-run` does not exist as a flag. Do not use it.
- Never run `./configure` / `make` for a pre-bump check.

### Lockfile

None.

### Extra update steps

None.

## vcpkg

### Detection

`vcpkg.json` at the project root.

### Version-bearing file

`vcpkg.json` allows exactly one of four mutually exclusive version fields. Check which one is present.

| Field | Scheme | Auto-bump |
|---|---|---|
| `"version"` | Relaxed, dot-separated, semver-like. The dominant default | Yes |
| `"version-semver"` | Strict SemVer 2.0.0 | Yes |
| `"version-date"` | `YYYY-MM-DD[.N]`, for "Live at HEAD" libraries | No, ask the user |
| `"version-string"` | Arbitrary, unordered, legacy-only | No, ask the user |

### Bump-rule nuance

For `"version"` / `"version-semver"`, apply the standard numeric patch-increment rule.

### Build/check

None separately. The underlying CMake/Meson/Autotools build covers it.

### Lockfile

None.

### Extra update steps

Reset the sibling `"port-version"` integer field to `0` whenever the version changes. This is vcpkg's documented rule.

## Conan

### Detection

`conanfile.py`. Ignore `conanfile.txt` entirely: it only lists dependencies and has no version field.

### Version-bearing file

Grep `conanfile.py` to decide which case applies:

(a) A static `version = "x.y.z"` class attribute → edit it.

(b) A `def set_version(self):` method → nothing to edit in `conanfile.py`. The source of truth is whatever file `set_version()` reads (commonly `CMakeLists.txt` or a plain `VERSION` file), which that file's own rule covers.

### Bump-rule nuance

`version` is semver-shaped by convention, not format-enforced. Apply the standard numeric patch-increment rule when the existing value is dotted-numeric.

### Build/check

None separately. The underlying CMake/Meson/Autotools build covers it.

### Lockfile

None.

### Extra update steps

None.

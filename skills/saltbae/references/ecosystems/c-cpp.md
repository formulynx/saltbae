# C / C++

CMake, Meson and Autotools are alternative build systems; if more than one is present, the consensus rule applies. vcpkg and Conan are additive manifests updated alongside them.

Contents: CMake · Meson · Autotools · vcpkg · Conan

## CMake

### Version-bearing file

`VERSION` in the top-level `project(... VERSION x.y.z ...)`.

### Build/check

`cmake --build <builddir>` if a build directory already exists; otherwise skip.

## Meson

### Version-bearing file

`version:` in the top-level `project(...)`.

### Build/check

`meson compile -C <builddir>` if a build directory already exists; otherwise skip.

## Autotools

### Detection

`configure.ac`, or legacy `configure.in`.

### Version-bearing file

The 2nd positional argument of `AC_INIT([package], [x.y.z], ...)`.

### Build/check

`autoreconf`. Never run `./configure` or `make`, and there is no `--dry-run` flag.

## vcpkg

### Version-bearing file

Exactly one of these fields is present:

| Field | Auto-bump |
|---|---|
| `"version"`, `"version-semver"` | Yes |
| `"version-date"`, `"version-string"` | No, ask the user |

### Build/check

Covered by the build system.

### Extra update steps

Reset `"port-version"` to `0` whenever the version changes.

## Conan

### Detection

`conanfile.py` only. `conanfile.txt` has no version.

### Version-bearing file

(a) A static `version = "x.y.z"` attribute → edit it.

(b) A `set_version(self)` method → edit the file it reads from instead.

### Build/check

Covered by the build system.

# PowerShell

## Module manifest

### Detection

(a) A module manifest `*.psd1`, named identically to its sibling module (script module `.psm1`, binary module `.dll`) in the same directory. This is how PowerShell links a manifest to its module.

(b) Loose `.ps1` scripts with no `.psd1` anywhere → no manifest. The project is tag-versioned, and the git tag is the primary source.

### Version-bearing file

The `.psd1` manifest's `ModuleVersion` key, the one mandatory field in the manifest.

A `.psd1` is a PowerShell Data file, a restricted-syntax hash-table literal, not JSON/TOML/YAML. Treat `ModuleVersion = 'x.y.z'` as a single-quoted `Key = 'value'` line for text replacement. Do not parse it with a JSON/TOML/YAML library.

### Bump-rule nuance

PowerShell's `[version]` type accepts 2–4 numeric segments with no suffix convention. Treat it as `MAJOR.MINOR.PATCH` and apply the standard numeric patch-increment rule.

### Build/check

`Test-ModuleManifest <path>.psd1`. It verifies that the manifest and its referenced files are consistent and errors on a malformed manifest.

### Lockfile

None.

### Extra update steps

None.

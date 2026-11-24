# PowerShell

## Module manifest

### Detection

(a) A `*.psd1` named after its sibling `.psm1` / `.dll`.

(b) Only loose `.ps1` scripts → tag-versioned.

### Version-bearing file

`ModuleVersion = 'x.y.z'` in the `.psd1`. Edit it as text; it is not JSON/TOML/YAML.

### Build/check

`Test-ModuleManifest <path>.psd1`.

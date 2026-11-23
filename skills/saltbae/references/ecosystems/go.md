# Go

## Go modules

### Detection

`go.mod` at the repo root, or at a subdirectory root for a nested module.

### Version-bearing file

None, by design. The project is tag-versioned, and the git tag is the primary source.

- Neither the `module` directive (the import path) nor the `go` directive (the minimum toolchain version) is a project version field. Do not add `go.mod` to the version-bearing-file list.
- Tags use the canonical form `vX.Y.Z`, always with the leading `v`.

### Bump-rule nuance

Standard PATCH/MINOR tag increments need no special handling. Crossing a MAJOR version boundary requires the extra update steps below. This applies to v1→v2 and any vN→vN+1 with N≥1, never to v0.x→v1.0.0.

### Build/check

`go build ./...` && `go vet ./...`.

### Lockfile

None. `go.sum` does not record the module's own version.

### Extra update steps

Only when crossing a MAJOR version boundary, in this exact order:

1. Edit the `module` line in `go.mod` to append or update the `/vN` suffix (e.g. `module example.com/mymodule` → `module example.com/mymodule/v2`).
2. Rewrite every internal `import "modulepath/..."` occurrence across all `.go` files to the new `modulepath/vN/...` form.
3. Only then create the `vN.0.0` git tag.

Skipping steps 1–2 and only re-tagging produces a broken module. The `go` command either rejects the mismatched tag or applies a legacy `+incompatible` marker that may break the build.

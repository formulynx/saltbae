# Go

## Go modules

### Version-bearing file

None; tag-versioned. Tags always carry the leading `v` (`vX.Y.Z`). The `module` and `go` directives are not versions.

### Build/check

`go build ./... && go vet ./...`.

### Extra update steps

Only when crossing a MAJOR boundary at v1 or above (never v0 → v1), in order:

1. Append or update the `/vN` suffix on the `module` line in `go.mod`.
2. Rewrite every internal import to the `/vN` path.
3. Then tag `vN.0.0`. Re-tagging alone produces a broken module.

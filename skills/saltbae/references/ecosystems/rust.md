# Rust

## Cargo

### Version-bearing file

- `[package].version`, or `[workspace.package].version` in a `[workspace]` manifest (including a virtual manifest).
- Leave members with `version.workspace = true` untouched. Only a member with its own literal `version` is versioned independently.

### Build/check

`cargo check`; `cargo check --workspace` when the file has a `[workspace]` section.

### Lockfile

Re-run the build/check command so `Cargo.lock` picks up the new version.

## Tauri

### Version-bearing file

`tauri.conf.json`'s `"version"`, kept in sync with the app's `package.json` and `Cargo.toml`. If the value is a path to a `package.json`, that file carries the version instead.

### Build/check

Covered by Cargo and npm.

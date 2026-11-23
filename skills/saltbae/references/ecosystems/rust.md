# Rust

## Cargo

### Detection

`Cargo.toml` at the repo root or in a subdirectory.

### Version-bearing file

- `version` in `[package]`.
- Or `version` in `[workspace.package]` when the file has a `[workspace]` section. A "virtual manifest" (`[workspace]` but no `[package]`) is still version-bearing if `[workspace.package].version` is present.
- Member crates that declare `version.workspace = true` inherit the root version at parse time. Do not edit them. Only a member with its own literal `version = "x.y.z"` is independently versioned.
- Skip a `Cargo.toml` entirely only when it has `[workspace]` and neither `[package].version` nor `[workspace.package].version` is present.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

- `cargo check` from the file's directory.
- `cargo check --workspace` whenever the file has a `[workspace]` section. Plain `cargo check` on a non-virtual workspace silently checks only the root crate and skips other members.

### Lockfile

Run the same `cargo check` command from the file's directory so `Cargo.lock` picks up the new version. The cache is warm from the build/check step, so this is fast.

### Extra update steps

None.

## Tauri

### Detection

`tauri.conf.json`, typically alongside a `package.json` and a `Cargo.toml` in the same app.

### Version-bearing file

`tauri.conf.json`'s `"version"` field. A Tauri app keeps `package.json`, `Cargo.toml` and `tauri.conf.json` in sync, so all three are updated together.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

None separately. The Cargo and npm build/check steps cover it.

### Lockfile

None.

### Extra update steps

None.

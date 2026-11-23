# Lua

## LuaRocks

### Detection

`*.rockspec` at the repo root.

### Version-bearing file

The rockspec's mandatory `version` field, format `"pkgversion-rockspecrevision"` (e.g. `"2.0.1-1"`: package version `2.0.1`, rockspec revision `1`).

### Bump-rule nuance

The `-rockspecrevision` part is exempt from the ask-the-user suffix rule in `SKILL.md`.

- Bump only the `pkgversion` part with the standard numeric patch-increment rule.
- Leave `-rockspecrevision` unchanged. Its reset/increment semantics relative to a package-version change are unconfirmed.

### Build/check

Skip. No reliable command is confirmed for this ecosystem.

### Lockfile

None.

### Extra update steps

None.

# Elixir

## Mix

### Detection

`mix.exs` at the repo root.

### Version-bearing file

The `version:` key inside `mix.exs`'s `def project do ... end` block (e.g. `version: "0.1.0"`).

If the key is not a literal string, check for indirection before giving up:

- A `@version` module attribute (`@version "0.2.0"` then `version: @version`) → edit the attribute.
- An external `VERSION` file read at compile time → edit that file.

### Bump-rule nuance

Apply the standard numeric patch-increment rule. No ecosystem-specific rule is confirmed.

### Build/check

Skip. No reliable command is confirmed for this ecosystem.

### Lockfile

None.

### Extra update steps

None.

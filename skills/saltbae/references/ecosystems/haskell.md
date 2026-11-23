# Haskell

## Cabal / hpack / Stack

### Detection

- `*.cabal` at the package root. Cabal is the base build/package format.
- `package.yaml`. hpack is a YAML front-end that generates the `.cabal` file.
- `stack.yaml`. Stack wraps Cabal packages and defers to the wrapped package's `.cabal` / `package.yaml` for the version. It has no version field of its own.

### Version-bearing file

(a) hpack in use → `package.yaml`'s top-level `version:` key (default `0.0.0` if omitted). hpack overwrites the `.cabal` file's version from it.

(b) Otherwise → the `.cabal` file's top-level `version:` field, required in every `.cabal` file.

### Bump-rule nuance

Apply the standard numeric patch-increment rule. No ecosystem-specific rule is confirmed.

### Build/check

Skip. No reliable command is confirmed for this ecosystem. Do not invent one.

### Lockfile

None.

### Extra update steps

None.

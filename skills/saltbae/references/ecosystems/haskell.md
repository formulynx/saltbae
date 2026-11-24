# Haskell

## Cabal / hpack / Stack

### Version-bearing file

(a) `package.yaml` present (hpack) → its `version:`. hpack regenerates the `.cabal` file from it.

(b) Otherwise → `version:` in the `.cabal` file.

`stack.yaml` has no version of its own.

### Build/check

Skip; no reliable command is confirmed.

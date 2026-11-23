# Shell / Bash

## Plain shell scripts

### Detection

Shell scripts (`*.sh`, `*.bash`) with no manifest from any other reference.

### Version-bearing file

None. No de-facto manifest convention exists for pure Shell projects. Prominent Shell projects either:

(a) carry a `package.json` purely as an npm-metadata wrapper, which `javascript.md` covers, or

(b) are tag-versioned with zero files touched. The git tag is the primary source.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

None. No universal build step exists for shell scripts. A `package.json` with its own `scripts` is covered by `javascript.md`.

### Lockfile

None.

### Extra update steps

None.

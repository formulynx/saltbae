# PHP

## Composer

### Detection

`composer.json` at the repo root.

### Version-bearing file

`composer.json`'s top-level `"version"` field, if present.

Its absence is normal, not a gap. Composer's docs discourage setting it for most (especially Packagist-published) projects, because the repository can infer the version from the VCS tag. Treat the git tag as a co-primary source:

(a) `"version"` present → use it.

(b) `"version"` absent → read the latest git tag. Do not treat the missing field as disagreement or an error.

### Bump-rule nuance

The version is semver-shaped (`MAJOR.MINOR.PATCH[-prerelease][+build]`). Composer's stability levels (dev, alpha, beta, RC) and branch-alias suffixes (`-dev`, `.x-dev`) are suffixes. Ask the user instead of incrementing through them.

Caret (`^`) / tilde (`~`) constraints in `require` blocks are dependency constraints, not the project's own version. Do not let them confuse the bump target.

### Build/check

`composer validate --strict`. It validates `composer.json` and, if `composer.lock` exists, checks that it is up to date. `--strict` turns warnings into a non-zero exit code. `composer install --dry-run` is an alternative.

### Lockfile

`composer.lock` present and `"version"` was edited → run `composer validate --strict` again. If it reports the lock file as out of date, run `composer update --lock` to refresh only the lock's content hash.

### Extra update steps

None.

# PHP

## Composer

### Version-bearing file

`composer.json`'s `"version"`, if present. Its absence is normal: the project is then tag-versioned, not in disagreement.

### Bump-rule nuance

Stability suffixes (`-dev`, `-alpha`, `-beta`, `-RC`, `.x-dev`) are suffixes. Ignore `require` constraints; they are not the project version.

### Build/check

`composer validate --strict`.

### Lockfile

`composer.lock` present and `"version"` edited → re-run `composer validate --strict`; if it reports the lock as outdated, run `composer update --lock`.

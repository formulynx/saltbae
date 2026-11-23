# Ruby

## RubyGems / Bundler

### Detection

(a) `*.gemspec` at the repo root → a library/gem project, version-bearing.

(b) `Gemfile` with no `.gemspec` → an application. `Gemfile` only declares dependency constraints and has no project-version field. The project is tag-versioned, and the git tag is the primary source.

(c) Both present → the `.gemspec` wins. The `Gemfile`'s `gemspec` directive only pulls in its dev/test dependencies.

### Version-bearing file

Check the gemspec for a literal first:

1. A literal `spec.version = "x.y.z"` (or `s.version = "..."`) in the gemspec → edit it. This is the minority/legacy pattern.
2. Else the gemspec references a constant (`spec.version = MyGem::VERSION`) → do not edit the gemspec. Edit `lib/<gem_name>/version.rb`'s `VERSION = "x.y.z"` constant. This is what `bundle gem <name>` scaffolds by default.

### Bump-rule nuance

RubyGems flags a gem as prerelease whenever the version contains a letter (`.pre`, `.rc1`, `.beta.3`, etc.). Treat any letter-bearing suffix as a suffix and ask the user instead of incrementing through it.

### Build/check

- `Rakefile` calls `Bundler::GemHelper.install_tasks` → `bundle exec rake build`.
- Otherwise → `gem build <gem_name>.gemspec --strict`. `--strict` turns spec-validation warnings into errors, catching a broken `version.rb` reference.

### Lockfile

`Gemfile.lock` present and the gemspec is loaded via the `gemspec` directive or a path/git dependency → run `bundle install` (or `bundle lock`) so the lock's `PATH` section picks up the new version.

### Extra update steps

None.

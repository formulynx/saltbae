# Ruby

## RubyGems / Bundler

### Detection

(a) `*.gemspec` → version-bearing.

(b) `Gemfile` without a gemspec → an application; tag-versioned.

### Version-bearing file

1. A literal `spec.version = "x.y.z"` in the gemspec → edit it.
2. Otherwise the gemspec references a constant → edit `VERSION` in `lib/<gem>/version.rb`, not the gemspec.

### Bump-rule nuance

Any letter in the version (`.pre`, `.rc1`, `.beta.3`) is a suffix.

### Build/check

`bundle exec rake build` when the Rakefile installs `Bundler::GemHelper` tasks; otherwise `gem build <gem>.gemspec --strict`.

### Lockfile

`Gemfile.lock` present and the gemspec is loaded via `gemspec` or a path dependency → `bundle lock`.

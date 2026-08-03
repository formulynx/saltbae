# Version ecosystems reference

Dispatched from `SKILL.md` Part 2 Step 1 (detect version files) and Step 2
(build/check) for every ecosystem beyond the 5 kept inline there (npm,
Cargo, `tauri.conf.json`, `pyproject.toml`, `CMakeLists.txt`). Read only the
section(s) matching files actually found in the repo — multiple ecosystems
can and do coexist in one repo; list and update every matching file in
sync, exactly as Step 1 already does for the inline 5.

Two policies from `SKILL.md` Step 1 apply uniformly to every ecosystem
below and are NOT repeated per-section: (1) if version-bearing files or
build systems disagree — including within one language, e.g. both
`CMakeLists.txt` and `meson.build` present mid-migration — stop and ask the
user which is canonical, never silently pick one; (2) only auto-increment
the patch number when the current version is a bare `MAJOR.MINOR.PATCH`
with no suffix — stop and ask the user for the intended next version
whenever a prerelease/build/snapshot suffix is present.

Each section below covers: detection signal, version-bearing file(s) +
exact field, bump-rule nuance (what NOT to auto-increment through), and the
pre-bump build/check command.

---

## PHP — Composer

- **Detection**: `composer.json` present at repo root.
- **Version-bearing file**: `composer.json`'s top-level `"version"` field,
  if present. **Its absence is normal, not a gap** — Composer's own docs
  discourage setting it for most (especially Packagist-published) projects
  ("In most cases this is not required and should be omitted... Optional if
  the package repository can infer the version from somewhere, such as the
  VCS tag name"). For Composer specifically, treat the git tag as a
  **co-primary** source, not a last-resort fallback: check
  `composer.json`'s `"version"` first and use it if present (no behavior
  change there); if absent, go straight to `git describe --tags
  --abbrev=0` with no surprise — do not treat the missing field as
  disagreement or an error state the way a missing field would be for
  other ecosystems.
- **Bump-rule nuance**: version is semver-shaped
  (`MAJOR.MINOR.PATCH[-prerelease][+build]`); apply the same numeric-patch
  rule as everywhere else. Composer recognizes five stability levels (dev,
  alpha, beta, RC, stable) and branch-alias suffixes (`-dev`, `.x-dev`) —
  treat any of these as a suffix requiring the ask-the-user rule, same as a
  semver prerelease. Caret (`^`)/tilde (`~`) pre-1.0 quirks in `composer.json`
  `require` blocks affect *dependency constraints*, not the project's own
  version — do not let those confuse the bump target.
- **Build/check**: `composer validate --strict` (validates `composer.json`
  and, if `composer.lock` exists, checks it's up to date; `--strict` turns
  warnings into a non-zero exit code) — or `composer install --dry-run`.

## Ruby — RubyGems

- **Detection**: `*.gemspec` present at repo root → library/gem project,
  version-bearing. `Gemfile` present with **no** `.gemspec` → this is an
  application, not a library; `Gemfile` only declares dependency
  *constraints* and carries no project-version field at all — fall straight
  through to the git-tag fallback, same as a manifest-less project. If both
  are present, the `.gemspec` wins; the `Gemfile`'s `gemspec` directive only
  pulls in its dev/test dependencies.
- **Version-bearing file**: the dominant convention (what `bundle gem
  <name>` scaffolds by default) is **indirect** — do NOT edit the
  `.gemspec` itself. Edit `lib/<gem_name>/version.rb`'s
  `VERSION = "x.y.z"` constant; the gemspec reads
  `spec.version = MyGem::VERSION` and picks up the new constant
  automatically at `gem build` time. Minority/legacy pattern: some gemspecs
  inline a literal `spec.version = "x.y.z"` (or `s.version = "..."`)
  directly with no `version.rb` — check for this literal first; only fall
  back to the `version.rb` indirection if the gemspec instead references a
  constant.
- **Bump-rule nuance**: standard semver. RubyGems flags a gem as
  "prerelease" whenever the version string contains a letter (`.pre`,
  `.rc1`, `.beta.3`, etc.) — treat any letter-bearing suffix as a suffix
  requiring the ask-the-user rule, never increment through it.
- **Build/check**: `bundle exec rake build` (when the `Rakefile` calls
  `Bundler::GemHelper.install_tasks`, this is the standard generated task);
  if there's no Rakefile/GemHelper setup, `gem build <gem_name>.gemspec
  --strict` instead (`--strict` turns spec-validation warnings into
  errors, catching a broken `version.rb` reference). Follow with `bundle
  install` to refresh `Gemfile.lock` if the gem is also consumed as a
  path/git dependency elsewhere in the same repo.

## Java / Kotlin — Maven

- **Detection**: `pom.xml` present at the project root (or nearest
  ancestor). Corroborating signal: `mvnw`/`mvnw.cmd` wrapper scripts.
- **Version-bearing file**: `pom.xml`'s `<version>` element that is a
  **direct child of the root `<project>` element** only — never
  `/project/parent/version` (the parent POM's own version, a different
  number used for inheritance) and never a `<dependencies>`/
  `<dependencyManagement>` `<version>` (a dependency constraint). A naive
  grep for `<version>` false-positives on both of those; parse for the
  first `<version>` that is a direct sibling of `<groupId>`/`<artifactId>`
  under the top-level `<project>` node. Multi-module reactor child POMs
  frequently omit their own `<version>` and inherit from `<parent>` — the
  version then genuinely lives only in the root/parent POM. **CI-friendly
  versions (Maven 3.5+)**: the root POM's `<version>` may be the literal
  placeholder `${revision}` (optionally with `${sha1}`/`${changelist}`
  too), with the real value in `<properties><revision>x.y.z</revision></properties>`
  in the same POM (or `.mvn/maven.config`) — when you see this placeholder,
  the version-bump target is the `<revision>` property's value, not the
  literal `<version>` text.
- **Bump-rule nuance**: standard semver, plus the `-SNAPSHOT` suffix
  denoting an in-development, unreleased version — this is a flag, not
  numeric content. Preserve `-SNAPSHOT` on a routine bump (e.g.
  `1.2.3-SNAPSHOT` → `1.2.4-SNAPSHOT`); only strip it on an explicit release
  cut (`1.2.3-SNAPSHOT` → `1.2.3`). Never treat "SNAPSHOT" as a token to
  increment.
- **Build/check**: `mvn -q -DskipTests compile` (or the lighter `mvn
  validate`).

## Java / Kotlin — Gradle

- **Detection**: any of `build.gradle`, `build.gradle.kts`,
  `settings.gradle`, `settings.gradle.kts` present at the project root.
  Corroborating signal: `gradlew`/`gradlew.bat` wrapper scripts. Kotlin
  projects disproportionately use the `.kts` variant — this doesn't change
  the detection check, which already treats any of the four files as "this
  is a Gradle project."
- **Version-bearing file**: priority order — (1) `gradle.properties`'s
  top-level `version=x.y.z` line first (this file loads before any build
  script executes); (2) else the inline `version = "x.y.z"` (Groovy) /
  `version = "x.y.z"` (Kotlin DSL) assignment in `build.gradle`/
  `build.gradle.kts` — `Project.version` defaults to the literal string
  `"unspecified"` if neither is set.
- **Bump-rule nuance**: standard semver, no ecosystem-specific suffix
  convention beyond the general rule above.
- **Build/check**: `./gradlew build -x test` (or `./gradlew check`).

## Scala — sbt

- **Detection**: `build.sbt` present at the project root. Corroborating
  (not itself a version file) signal: `project/build.properties`, which
  pins the sbt *launcher* version (`sbt.version`), not the project's own
  version — do not misread it as a version-bump target.
- **Version-bearing file**: priority order — (1) a dedicated `version.sbt`
  file first, if present (the `sbt-release` plugin's convention: it writes
  the release/development version to this file, defaulting to a single
  `version := "x.y.z"` or `ThisBuild / version := "x.y.z"` line, and never
  touches other build-definition files); (2) else the `version :=` /
  `ThisBuild / version :=` line inside `build.sbt` directly.
- **Bump-rule nuance**: standard semver plus the same `-SNAPSHOT` suffix
  convention as Maven (sbt routes snapshot vs. release artifacts to
  different repositories based on this suffix) — preserve or strip only on
  an explicit release cut, exactly like the Maven rule above; never treat
  it as numeric content.
- **Build/check**: `sbt compile`.

## Go modules

- **Detection**: `go.mod` present at the repo root (or a subdirectory root
  for a nested module).
- **Version-bearing file**: **none, by design** — neither the `module`
  directive (the import path) nor the `go` directive (the minimum
  toolchain version) is a project version field. Go modules version
  **exclusively via git tags**, in canonical form `vX.Y.Z` (always with the
  leading `v`, unlike npm/Cargo's bare form). Treat the existing git-tag
  fallback (`git describe --tags --abbrev=0`) as the correct **primary**
  mechanism for Go, not a fallback of last resort — do not add `go.mod` to
  the version-bearing-file list.
- **Bump-rule nuance — hard rule, not a suggestion**: standard PATCH/MINOR
  tag increments need no special handling. **Crossing a MAJOR version
  boundary** (v1→v2+, or vN→vN+1 for any N≥1; this never applies to
  v0.x→v1.0.0) additionally requires, in this exact order:
  1. Edit the `module` line in `go.mod` to append/update the `/vN` suffix
     (e.g. `module example.com/mymodule` → `module example.com/mymodule/v2`).
  2. Rewrite every internal `import "modulepath/..."` occurrence across all
     `.go` files to the new `modulepath/vN/...` form.
  3. Only then create the `vN.0.0` git tag.

     Skipping steps 1–2 and only re-tagging produces a broken module — the
     `go` command will either reject the mismatched tag or silently apply a
     legacy `+incompatible` marker that "may break the build."
- **Build/check**: `go build ./...` && `go vet ./...`.

## Shell / Bash

- **Detection / version-bearing file**: no de-facto manifest convention
  exists for pure Shell projects — this is an intentional non-finding, not
  a gap. Prominent Shell-language GitHub projects either (a) already carry
  a `package.json` purely as an npm-metadata wrapper (already covered by
  the existing `package.json` rule), or (b) version purely via plain git
  tags with zero files touched. No new detection rule is added; the
  existing `package.json` check plus the git-tag fallback already cover
  every case observed.
- **Bump-rule nuance**: none beyond the general rule — whichever source
  fires (`package.json` or git tag) uses its own already-stated rule.
- **Build/check**: none — no universal "build" step exists for shell
  scripts. If a detected `package.json` has its own `scripts`, that's
  already covered by the npm row; otherwise skip.

## C/C++ — Meson

- **Detection**: `meson.build` present at the project root. Meson,
  Autotools, and CMake (`CMakeLists.txt`, handled inline in `SKILL.md`) are
  alternative primary build systems for the same language — apply the
  cross-cutting consensus rule (top of this file) if more than one is
  present in the same repo (e.g. a mid-migration project), rather than
  silently preferring one.
- **Version-bearing file**: the top-level `meson.build`'s `project(...)`
  call's `version:` keyword argument, e.g. `project('gtk+', 'c', version:
  '3.94.0', ...)`.
- **Bump-rule nuance**: the `version:` value is documented as a free-form
  string (no built-in semver enforcement), but the overwhelming real-world
  convention is dotted `MAJOR.MINOR.PATCH` — apply the standard numeric
  patch-increment rule.
- **Build/check**: `meson compile -C <builddir>` if a build directory
  already exists from prior development; otherwise skip (same "don't
  bootstrap from scratch" precedent as `pyproject.toml`/CMake).

## C/C++ — Autotools

- **Detection**: `configure.ac` present (or the legacy `configure.in`
  filename — both accepted by `autoconf`/`autoreconf`, but `configure.ac`
  is the current convention). Same consensus rule as Meson if this
  coexists with `CMakeLists.txt`/`meson.build`.
- **Version-bearing file**: `configure.ac`'s `AC_INIT([package], [x.y.z],
  [bug-report-address], ...)` macro call — the version is the **2nd
  positional argument**, a bare string with no key name (e.g.
  `AC_INIT([amhello], [1.0], [bug-automake@gnu.org])`).
- **Bump-rule nuance**: unconstrained string per the Autoconf manual, but
  real-world Autotools projects overwhelmingly use dotted numeric
  versions — apply the standard numeric patch-increment rule.
- **Build/check**: `autoreconf` (or plain `autoconf` alone) — **not**
  `autoreconf --dry-run`, which does not exist as a flag (confirmed absent
  from the documented option list). `autoreconf`/`autoconf` regenerate
  `configure`/`Makefile.in` from `configure.ac`/`Makefile.am`, catching
  M4/Automake syntax errors, without running `./configure` or `make` and
  thus without mutating the working tree. Never run `./configure`/`make`
  themselves for a pre-bump check.

## C/C++ — vcpkg.json

- **Detection**: `vcpkg.json` present at the project root. This is
  ADDITIVE, not an alternative — it's a dependency-manifest for the vcpkg
  package manager, normally coexisting alongside CMakeLists.txt/
  meson.build/configure.ac, which remain the actual build driver. Add it
  to the "list every file found — all updated in sync" set.
- **Version-bearing file**: `vcpkg.json` allows **exactly one** of four
  mutually-exclusive version fields — check which one is present:
  - `"version"` — relaxed, dot-separated, semver-like; this is the
    dominant/default scheme (appears in essentially all official examples).
  - `"version-semver"` — strict SemVer 2.0.0.
  - `"version-date"` — `YYYY-MM-DD[.N]` form, for "Live at HEAD" libraries.
  - `"version-string"` — arbitrary, unordered, legacy-only ("all ports
    created before the other version fields were introduced use this
    scheme") — do not auto-bump this one; ask the user instead, since it's
    non-numeric/unordered by design.
- **Bump-rule nuance**: for `"version"`/`"version-semver"`, apply the
  standard numeric patch-increment rule. **Always also reset the sibling
  `"port-version"` integer field to `0`** whenever the version itself
  changes — this is vcpkg's own documented rule ("reset to 0 each time the
  version of the package is updated").
- **Build/check**: none separately — the underlying CMake/Meson/Autotools
  build (whichever is present) already covers it.

## C/C++ — Conan (conanfile.py)

- **Detection**: `conanfile.py` present. `conanfile.txt` has **no**
  version field of its own (it only lists dependencies, and "cannot be
  used to create a package") — ignore `conanfile.txt` entirely for version
  purposes. ADDITIVE alongside CMakeLists.txt/meson.build/configure.ac,
  same as vcpkg.json.
- **Version-bearing file**: `conanfile.py`'s `version = "x.y.z"` class
  attribute, if it's a static literal. **If instead the file defines a
  `def set_version(self):` method**, there is nothing to edit in
  `conanfile.py` at all — the real source of truth is whatever file
  `set_version()` reads (commonly `CMakeLists.txt` or a plain `VERSION`
  file), which is already covered by that file's own rule. Detect which
  case applies with a simple grep for a static `version = "..."` attribute
  vs. a `def set_version(self):` method definition.
- **Bump-rule nuance**: `version` is semver-shaped by convention (not
  format-enforced beyond a generic identifier regex) — apply the standard
  numeric patch-increment rule when the existing value is already
  dotted-numeric.
- **Build/check**: none separately — same reasoning as vcpkg.json.

## C# / .NET

- **Detection**: any `*.csproj`/`*.fsproj`/`*.vbproj` at any depth
  (excluding `bin/`/`obj/`). Also check for `Directory.Build.props` at the
  solution/repo root — when present and it defines `<Version>`/
  `<VersionPrefix>`, treat it as the single canonical file to bump instead
  of editing the same property redundantly in every individual project
  file (MSBuild walks upward from each project directory and applies the
  first `Directory.Build.props` it finds to all projects under it).
- **Version-bearing file(s) + field, in priority order**:
  1. `<Version>` — single MSBuild property, the full semver string
     including any prerelease suffix (e.g. `1.2.3-beta.1`) — canonical
     when present.
  2. `<VersionPrefix>` / `<VersionSuffix>` — split form: `VersionPrefix`
     is the base numeric semver, `VersionSuffix` is the prerelease label;
     MSBuild composes these into `$(Version)` (`VersionPrefix` alone, or
     `VersionPrefix-VersionSuffix` if a suffix is set) **only when
     `$(Version)` itself isn't explicitly set**. Bump `VersionPrefix` when
     this split form is used instead of a literal `<Version>`.
  3. `<AssemblyVersion>` / `<FileVersion>` (or, in older non-SDK-style
     projects, `[assembly: AssemblyVersion("...")]` /
     `[assembly: AssemblyFileVersion("...")]` attributes in
     `AssemblyInfo.cs`) — a **4-part, NOT semver** Windows-style version
     (`Major.Minor.Build.Revision`). Leave these **out of scope** for an
     automatic bump unless a repo is already manually keeping them
     numerically in sync with `<Version>`.
  4. Standalone `.nuspec`'s `<version>` element — only relevant for legacy
     non-SDK-style projects (modern SDK-style projects auto-generate the
     `.nuspec` at pack time from `<Version>`, so a hand-authored `.nuspec`
     signals a legacy project). Add it to the sync set if present.
- **Bump-rule nuance**: apply the standard numeric patch-increment rule to
  whichever of tiers 1/2 is canonical; never touch tier 3's 4-part fields
  as part of a routine bump unless they're already tracked in lockstep.
- **Build/check**: `dotnet build` (or `dotnet build -c Release`).

## Swift — SwiftPM / CocoaPods / Xcode

- **Detection**: three independent, coexisting signals — check all three,
  since a real repo commonly has more than one:
  - `Package.swift` present → also (or purely) a Swift Package (SPM).
  - `*.podspec` present → also distributed via CocoaPods.
  - `*.xcodeproj`/`*.xcworkspace` present → has an Xcode-native target.
  These are not mutually exclusive — update whichever are actually
  present, in sync, same as `package.json` + `Cargo.toml` coexisting today.
- **Version-bearing file(s) + field**:
  - `Package.swift` (SPM) — **no version field at all, by design**. The
    `Package` initializer has no `version` parameter; SwiftPM versions
    purely via git tags (SemVer-formatted, `1.0.0` or `v1.0.0`), matching
    Go's git-tag-only model. For a pure-SPM package, "detect current
    version" falls straight to the git-tag fallback; "bump" means tagging,
    with no file diff at all.
  - `*.podspec` (CocoaPods) — `spec.version = 'x.y.z'`, a required field,
    root specification only (not writable on sub-specs).
  - Xcode (`.xcodeproj`/`.xcworkspace`) — **check both of these forms,
    whichever is actually present**:
    - Modern (Xcode 11+): the `MARKETING_VERSION` build setting inside
      `project.pbxproj` (one value per build configuration — update all
      occurrences), substituted into `Info.plist`'s
      `CFBundleShortVersionString` via the literal string
      `$(MARKETING_VERSION)`. If found, this is the value to bump.
    - Legacy: `Info.plist`'s `CFBundleShortVersionString` holds the
      version as a **hardcoded literal** directly (no `$(...)`
      indirection) — edit it in place if `MARKETING_VERSION` is absent
      from `project.pbxproj`.
    - If `Info.plist` contains the literal string `$(MARKETING_VERSION)`
      but no `MARKETING_VERSION` key exists anywhere in
      `project.pbxproj`, that's an inconsistent/broken project — flag it
      for the user rather than guessing.
    - **Never confuse either form with `CURRENT_PROJECT_VERSION` /
      `CFBundleVersion`** — that pair is a build number (analogous to
      Dart's `+buildNumber`), incremented per build/submission,
      independent of the marketing/short version. Do not bump it.
- **Bump-rule nuance**: standard semver for all three mechanisms — apply
  the numeric patch-increment rule to whichever files are present.
- **Build/check**: SPM → `swift build`. Xcode → `xcodebuild -list -json
  [-project X.xcodeproj | -workspace X.xcworkspace]` to enumerate targets/
  schemes/configurations deterministically, then `xcodebuild build
  -scheme <resolved-scheme> -quiet` — **known limitation**: picking which
  scheme is "the one to build" when several exist is not mechanically
  solvable from the JSON alone; ask the user, same as the ambiguous-version
  pattern elsewhere in this skill. CocoaPods → `pod lib lint`.

## Objective-C

Shares Swift's Xcode/CocoaPods detection and version-bearing files
entirely — build settings and `Info.plist` are attached to a target, not
to a source language, and a `.podspec` describes a Pod's public interface
regardless of whether `source_files` matches `.m` or `.swift`. No separate
detection rule, version file, bump rule, or build/check command is needed;
follow the Swift section above unchanged.

## Dart / Flutter

- **Detection**: `pubspec.yaml` present at the repo root (or package root
  in a monorepo/melos workspace) — the sole manifest format for both plain
  Dart and Flutter packages.
- **Version-bearing file**: `pubspec.yaml`'s top-level `version:` key,
  format `major.minor.patch[+buildNumber]` (e.g. `1.2.3+45`). The `+N`
  build-number suffix maps to Android's `versionCode`/iOS's
  `CFBundleVersion` at Flutter build time (`--build-number`), distinct
  from the `major.minor.patch` part which maps to `versionName`/
  `CFBundleShortVersionString` (`--build-name`).
- **Bump-rule nuance**: bump only the `major.minor.patch` part using the
  standard numeric patch-increment rule; **leave `+buildNumber` unchanged**
  — dart.dev's own docs have no bump policy for this suffix, and it's
  commonly CI-managed out-of-band, so touching it risks colliding with
  external build numbering. If the current version has no `+N` at all,
  don't introduce one.
- **Build/check**: `flutter build` for Flutter apps; `dart pub get && dart
  analyze` for pure-Dart packages.

## PowerShell

- **Detection**: a module manifest `*.psd1`, named identically to its
  sibling module (script module `.psm1`, binary module `.dll`) in the same
  directory — this is how PowerShell links a manifest to its module. A
  repo of loose `.ps1` scripts with no `.psd1` anywhere has no manifest at
  all — same "no convention, fall back to git tag" situation as Shell.
- **Version-bearing file**: the `.psd1` manifest's `ModuleVersion` key —
  the one genuinely mandatory field in an otherwise all-optional manifest.
  A `.psd1` is a **PowerShell Data file**, not JSON/TOML/YAML — a
  restricted-syntax hash-table literal. Treat `ModuleVersion = 'x.y.z'` as
  a single-quoted-string `Key = 'value'` line for safe text-replacement;
  do not attempt to parse it with a JSON/TOML/YAML library.
- **Bump-rule nuance**: treat as `MAJOR.MINOR.PATCH` and apply the
  standard purely-numeric patch-increment rule (PowerShell's `[version]`
  type accepts 2–4 numeric segments; no suffix convention to preserve).
- **Build/check**: `Test-ModuleManifest <path>.psd1` — a native validator
  that verifies the manifest and its referenced files are consistent;
  non-zero-exit/error on a malformed manifest, exit-code-checkable the same
  way as `cargo check`.

## Bonus — Haskell

- **Detection**: `*.cabal` present at the package root (Cabal, the base
  build/package format), or `package.yaml` (hpack — a YAML front-end that
  *generates* the `.cabal` file), or `stack.yaml` (Stack — wraps Cabal
  packages, defers to the wrapped package's `.cabal`/`package.yaml` for
  version, introduces no version field of its own).
- **Version-bearing file**: the `.cabal` file's top-level `version:` field
  (required in every `.cabal` file). For hpack, `package.yaml`'s top-level
  `version:` key (default `0.0.0` if omitted) — hpack generates/overwrites
  the `.cabal` file's version from this.
- **Bump-rule nuance**: numeric-patch default (unconfirmed as an
  ecosystem-specific rule — treated as low-risk default, same as
  everything else in this file).
- **Build/check**: skip — no reliable command confirmed for this
  ecosystem; do not invent one.

## Bonus — Elixir

- **Detection**: `mix.exs` present at the repo root — the Mix build
  tool's project file, universal for Elixir projects.
- **Version-bearing file**: inside `mix.exs`'s `def project do ... end`
  block, the `version:` key (e.g. `version: "0.1.0"`). Watch for
  indirection: some projects use a `@version` module attribute
  (`@version "0.2.0"` then `version: @version`) or an external `VERSION`
  file read at compile time instead of an inline literal — if the direct
  key isn't a literal string, check for these before giving up.
- **Bump-rule nuance**: numeric-patch default (unconfirmed as an
  ecosystem-specific rule, same low-risk-default treatment as Haskell).
- **Build/check**: skip — no reliable command confirmed for this
  ecosystem.

## Bonus — Lua

- **Detection**: `*.rockspec` present at the repo root — the LuaRocks
  package spec format.
- **Version-bearing file**: the rockspec's mandatory `version` field,
  format `"pkgversion-rockspecrevision"` (e.g. `"2.0.1-1"` — package
  version `2.0.1`, rockspec revision `1`).
- **Bump-rule nuance**: bump only the `pkgversion` part with the standard
  numeric patch-increment rule; **leave the trailing `-rockspecrevision`
  suffix unchanged by default** — its exact reset/increment semantics
  relative to a package-version change are unconfirmed.
- **Build/check**: skip — no reliable command confirmed for this
  ecosystem.

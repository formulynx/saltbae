---
name: saltbae
description: Carves uncommitted changes into properly-sized logical commits, using planning docs (plan files, CLAUDE.md, README, implementation plans) as grounds for grouping, and seasons each with a clear commit message. With the `bump` argument, also bumps the project version, builds, commits and tags the release. It auto-detects the version-bearing file(s) across a broad range of language ecosystems (npm/Node, Cargo/Rust, Tauri, Python, Java/Kotlin/Scala, Go, Ruby, PHP, C/C++, C#/.NET, Swift/Objective-C, Dart/Flutter, PowerShell, and more) and syncs matching version references in other files (README, install scripts, etc.). Use when the user wants to organize/split/commit working-tree changes, or cut a version bump / release tag.
argument-hint: "[bump [x.y.z]]"
---

# Saltbae — carve changes into well-seasoned commits

## Input

Arguments: $ARGUMENTS

- Empty → **default mode**: Part 1 only.
- `bump` or `bump <version>` → **bump mode**: Part 1, then Part 2. If `<version>` is given (e.g. `v4.2.1` or `4.2.1`), strip the leading `v` and use it; otherwise auto-increment the patch number.

## AI attribution

Follow Claude Code's `attribution.commit` setting as conveyed in its own instructions: add exactly the attribution it asks for, or none when it asks for none. This skill neither adds attribution of its own nor strips attribution the setting requires.

## Part 1 — Carve & Season

### 1. Check working tree

Run `git status`. If clean: in default mode, report "nothing to commit" and stop; in bump mode, continue to Part 2.

### 2. Gather grouping evidence

Map each change to the work it belongs to. Check existence before reading, and read only what plausibly relates to the diff.

1. A planning directory at the repo root (e.g. `.planning/`, `plans/`, `docs/plans/`): state files, current phase/plan files (`PLAN*.md`, `SUMMARY*.md`), roadmap if needed.
2. Otherwise, or as a supplement: `CLAUDE.md`, `AGENTS.md`, `README.md`, `IMPLEMENTATION_PLAN*.md`, `PLAN*.md`, `PLANNING*.md`, `TODO*.md`, `ROADMAP*.md`, `docs/` design docs, and issue references in the branch name.
3. Always: the current conversation, `git log --oneline -15` (message style and granularity), and the diffs themselves.

### 3. Group and split

- One commit = one reviewable unit (a feature, a fix, a refactor, a docs update), mapping to exactly ONE release-note category of Part 2 step 8. A change that both adds a feature and fixes a bug → two commits.
  - Exception: if one half alone would not build or type-check (entangled in the same function, or dependent on the other's type change), keep one commit and classify it by its dominant purpose. Judge this by reading the code; do not run builds per split candidate.
- Test files go with the code they test.
- Match the repository's commit message style (prefixes, language, phase notation) and follow any commit rules in its CLAUDE.md.

### 4. Commit

Stage and commit each group in order with `git add <specific paths>`, never `git add -A`.

**The working tree is read-only during Part 1.** Never write to a file in the repository's working tree to build a commit: no editing a file down to a partial state, no copying an intermediate version over it, no moving it aside and restoring it afterwards — even if the final content would end up identical. Every intermediate state exists only in the index.

**Splitting within a file.** When one file contains changes belonging to different commits, build each commit's version of that file in the index:
- Default: extract only the relevant hunks into a patch and stage them with `git apply --cached <patch>`, the way a human uses `git add -p`.
- If the hunks cannot be separated cleanly: write the intended intermediate content to a scratch file and stage it with `git update-index --cacheinfo 100644,$(git hash-object -w <scratch-file>),<path>`.

Scratch files (patches, intermediate contents) go in the scratchpad, outside the repository, and are only ever read by `git apply --cached` / `git hash-object`. Never copy them into the working tree.

**Verify the working tree was not touched.** Before the first `git add`, record a content hash of every changed or untracked file (e.g. `git ls-files -z -m -o --exclude-standard | xargs -0 shasum`). After the last commit, recompute it for the same paths and confirm it matches. A mismatch means a working-tree file was modified: stop and report which file.

**Commit message** — write it like a human maintainer, not a completion report:
- Subject: imperative mood, ≤50 chars where possible (72 hard ceiling), no trailing period.
- Body, only when the subject does not already convey the *why*: blank line, wrapped at ~72 columns, stating what changed and why. Keep it to a handful of lines.
- Never include: test/build output or commands run, file-by-file listings, step-by-step *how*, edge-case narration, or deferred-work rationale. If the project keeps plan/summary files, reference them instead.
- Matching the repo's style governs form only, not length or content.

### 5. Report

Print the commits created (hash, message, files) and anything left uncommitted, with the reason.

In default mode, stop here.

## Part 2 — Bump (only in bump mode)

Follow strictly in order. Stop immediately if any step fails.

### 1. Detect version files and current version

Search the repo for the detection patterns below, at the root and in subdirectories, excluding `.git/` and dependency/build-output directories (`node_modules/`, `target/`, `dist/`, `build/`, `bin/`, `obj/`, `vendor/`). For each pattern found, read the matching file under `references/ecosystems/`, and only those. Each reference defines, per tool: detection, version-bearing file and field, bump-rule nuance, build/check, lockfile, and extra update steps; an omitted section means nothing to do.

| Detection pattern | Reference |
|---|---|
| `package.json` | `javascript.md` |
| `Cargo.toml`, `tauri.conf.json` | `rust.md` |
| `pyproject.toml`, `setup.cfg`, `setup.py` | `python.md` |
| `CMakeLists.txt`, `meson.build`, `configure.ac`, `configure.in`, `vcpkg.json`, `conanfile.py` | `c-cpp.md` |
| `composer.json` | `php.md` |
| `*.gemspec`, `Gemfile` | `ruby.md` |
| `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`, `settings.gradle.kts` | `java-kotlin.md` |
| `build.sbt` | `scala.md` |
| `go.mod` | `go.md` |
| `*.csproj`, `*.fsproj`, `*.vbproj`, `Directory.Build.props`, `*.nuspec` | `dotnet.md` |
| `Package.swift`, `*.podspec`, `*.xcodeproj`, `*.xcworkspace` | `swift-objc.md` |
| `pubspec.yaml` | `dart.md` |
| `*.psd1`, `*.ps1` | `powershell.md` |
| `*.cabal`, `package.yaml`, `stack.yaml` | `haskell.md` |
| `mix.exs` | `elixir.md` |
| `*.rockspec` | `lua.md` |
| `*.sh`, `*.bash` with none of the above | `shell.md` |

List every version-bearing file found. ALL of them will be updated in sync, including across different ecosystems coexisting in one repo (e.g. a Tauri app has `package.json` + `Cargo.toml` + `tauri.conf.json`; a C++ project may have `CMakeLists.txt` alongside `vcpkg.json`).

- **Consensus rule**: if all detected files/build-systems agree on the current version, use it. If they disagree, including within a single language (e.g. a C++ repo mid-migration with both `CMakeLists.txt` and `meson.build`), stop and ask the user which is canonical. Never silently prefer one file/build-system over another via a fixed priority order; a strict override risks updating the wrong file during a migration.
- **Git-tag source**: if no version-bearing file is found, derive the current version from the latest git tag: `git describe --tags --abbrev=0` (strip a leading `v` for the numeric version). When a reference says the project is tag-versioned, this git-tag read is the expected **primary** mechanism, not a gap. If there is also no tag, stop and ask the user for the current version.
- Compute the new version. **Patch increment is purely numeric**: `0.4.9` → `0.4.10`, NOT `0.5.0`. MINOR and MAJOR never change on auto-increment.
- **Suffix/prerelease preservation**: only apply the auto-increment above when the detected version is a bare `MAJOR.MINOR.PATCH` with no suffix. When a suffix marker is present (e.g. a semver prerelease/build-metadata tag such as `-beta.1` or `+build5`, or an ecosystem-specific marker listed in its reference), stop and ask the user what the intended next version is, instead of incrementing through it. Exception: a suffix that the reference's bump-rule nuance explicitly says to preserve is kept unchanged while the numeric part is auto-incremented.
- Validate semver format (MAJOR.MINOR.PATCH). Print the transition (e.g., `0.3.14 → 0.3.15`).
- Record `PREV_TAG` for step 8's release notes: the tag `v{OLD_VERSION}`, if it exists (`git rev-parse -q --verify v{OLD_VERSION}`). If it doesn't exist, this is the first release — there is no `PREV_TAG`, and step 8 covers full history instead.

### 2. Build / check (before version update)

For each tool detected in step 1, run the command in its reference's **Build/check** section, from each file's directory. Where the reference says to skip, skip. This step never bootstraps a project from scratch.

If anything fails, stop and report. The version has not been changed yet, so re-running after a fix is safe.

### 3. Update version in ALL detected files

Use the Edit tool to update the version string in every file found in step 1, then apply each reference's **Extra update steps**, if any. Do NOT touch any other fields.

### 4. Update other version references

`git grep -nF` the OLD version in both bare (`0.1.0`) and `v`-prefixed (`v0.1.0`) forms. Outside the files from step 3, update genuine pins (README install lines and badges, install-script refs, CDN URLs). Leave historical records (CHANGELOG, past release notes) and lockfiles alone. If a match is ambiguous, ask the user.

### 5. Update lockfiles

For each tool whose files changed in step 3, run its reference's **Lockfile** procedure from the file's directory.

### 6. Commit

Stage ONLY the files from steps 3, 4 and 5, and commit with:

```
chore: bump version to {VERSION}
```

### 7. Tag

```
git tag -a v{VERSION} -m "v{VERSION}"
```

### 8. Generate release notes

Print only; never post anywhere.

- Range: `PREV_TAG..HEAD`, excluding the bump commit. With no `PREV_TAG`, cover full history and label it "Initial release".
- One bullet per commit: its subject line, verbatim or lightly smoothed. Merge trivially related commits (e.g. a fix right after what it fixes).
- Classify each commit into exactly ONE category, in this output order: `## Added` / `## Changed` / `## Fixed` / `## Removed` / `## Performance` / `## Documentation` / `## Security`.
  - Use the prefix if present (`feat:`→Added, `fix:`→Fixed, `perf:`→Performance, `docs:`→Documentation); otherwise the dominant purpose.
  - Tie-break: Security > Fixed > Added > Removed > Performance > Documentation > Changed (Changed is the catch-all).
  - Exclude pure maintenance (version bumps, CI config, lockfile-only).
- Omit empty categories. Output plain Markdown with no surrounding commentary.

### 9. Done

Print:
- Old version → new version
- Files updated
- Commit hash (short) and tag name
- The release notes in a fenced block
- A reminder to `git push && git push --tags` when ready

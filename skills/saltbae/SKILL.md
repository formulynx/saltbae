---
name: saltbae
description: Carves uncommitted changes into properly-sized logical commits, using planning docs (plan files, CLAUDE.md, README, implementation plans) as grounds for grouping, and seasons each with a clear commit message. With the `bump` argument, also bumps the project version, builds, commits and tags the release. It auto-detects the version-bearing file(s) across a broad range of language ecosystems (npm/Node, Cargo/Rust, Tauri, Python, Java/Kotlin/Scala, Go, Ruby, PHP, C/C++, C#/.NET, Swift/Objective-C, Dart/Flutter, PowerShell, Claude Code plugins, and more) and syncs matching version references in other files (README, install scripts, etc.). Use when the user wants to organize/split/commit working-tree changes, or cut a version bump / release tag.
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

`scripts/versions.py` (in this skill's base directory; Python 3.8+) handles detection, tool checks and verification. Run it from the repo root with `python3 <skill-dir>/scripts/versions.py <subcommand>`; it prints JSON. If `python3` is unavailable, do the same work by hand using the table in step 1, skipping `.git/`, `node_modules/`, `target/`, `dist/`, `build/`, `bin/`, `obj/` and `vendor/`.

### 1. Detect version files and current version

Run `versions.py detect`. Each entry in `files` has a `status`:

| `status` | Meaning | Action |
|---|---|---|
| `ok` | Literal version found | Bump it |
| `unresolved` | Behind an indirection (see `note`) | Resolve it with the reference |
| `tag-versioned` | No version file by design | Use the git tag |
| `inconsistent` | One file holds conflicting values | Ask the user |

Read every reference listed in `references`, and only those. Each covers, per tool: detection, version-bearing file, bump-rule nuance, build/check, lockfile, and extra update steps; an omitted section means nothing to do. Apply the references on top of the script output: e.g. a monorepo rule may exclude some `package.json` files, and an unresolved entry may point to a different file.

| Detection pattern | Reference |
|---|---|
| `package.json`, `lerna.json` | [references/ecosystems/javascript.md](references/ecosystems/javascript.md) |
| `Cargo.toml`, `tauri.conf.json` | [references/ecosystems/rust.md](references/ecosystems/rust.md) |
| `pyproject.toml`, `setup.cfg`, `setup.py` | [references/ecosystems/python.md](references/ecosystems/python.md) |
| `CMakeLists.txt`, `meson.build`, `configure.ac`, `configure.in`, `vcpkg.json`, `conanfile.py` | [references/ecosystems/c-cpp.md](references/ecosystems/c-cpp.md) |
| `composer.json` | [references/ecosystems/php.md](references/ecosystems/php.md) |
| `*.gemspec`, `Gemfile` | [references/ecosystems/ruby.md](references/ecosystems/ruby.md) |
| `pom.xml`, `build.gradle(.kts)`, `settings.gradle(.kts)` | [references/ecosystems/java-kotlin.md](references/ecosystems/java-kotlin.md) |
| `build.sbt` | [references/ecosystems/scala.md](references/ecosystems/scala.md) |
| `go.mod` | [references/ecosystems/go.md](references/ecosystems/go.md) |
| `*.csproj`, `*.fsproj`, `*.vbproj`, `Directory.Build.props`, `*.nuspec` | [references/ecosystems/dotnet.md](references/ecosystems/dotnet.md) |
| `Package.swift`, `*.podspec`, `*.xcodeproj` | [references/ecosystems/swift-objc.md](references/ecosystems/swift-objc.md) |
| `pubspec.yaml` | [references/ecosystems/dart.md](references/ecosystems/dart.md) |
| `*.psd1`, `*.ps1` | [references/ecosystems/powershell.md](references/ecosystems/powershell.md) |
| `*.cabal`, `package.yaml`, `stack.yaml` | [references/ecosystems/haskell.md](references/ecosystems/haskell.md) |
| `mix.exs` | [references/ecosystems/elixir.md](references/ecosystems/elixir.md) |
| `*.rockspec` | [references/ecosystems/lua.md](references/ecosystems/lua.md) |
| `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | [references/ecosystems/claude-plugin.md](references/ecosystems/claude-plugin.md) |
| `*.sh`, `*.bash` with none of the above | [references/ecosystems/shell.md](references/ecosystems/shell.md) |

All version-bearing files are updated in sync, across ecosystems (e.g. a Tauri app's `package.json` + `Cargo.toml` + `tauri.conf.json`).

- **Consensus**: `consensus: true` means every file agrees on `MAJOR.MINOR.PATCH`. Otherwise — including two build systems of one language mid-migration — ask the user which is canonical. Never pick one by a fixed priority.
- **Git tag**: with no version file, or when every entry is `tag-versioned`, use `latest_tag` (strip a leading `v`). No tag either → ask the user for the current version.
- **New version**: patch increment is purely numeric (`0.4.9` → `0.4.10`, not `0.5.0`); MINOR and MAJOR never change on auto-increment.
- **Suffixes**: auto-increment only a bare `MAJOR.MINOR.PATCH`. For any suffix (`-beta.1`, `+build5`, or one a reference lists), ask the user for the next version — unless the reference says to preserve that suffix, in which case increment the numeric part and keep it.
- Validate the result as `MAJOR.MINOR.PATCH` and print the transition (e.g. `0.3.14 → 0.3.15`).
- Record `PREV_TAG` = `v{OLD_VERSION}` if `git rev-parse -q --verify v{OLD_VERSION}` succeeds; otherwise there is none and step 8 covers full history.

### 2. Build / check (before version update)

1. Run `versions.py tools`. If `missing` is non-empty, stop and ask the user whether to install the command or skip the checks that need it. Do not substitute a different tool.
2. For each tool, run its reference's **Build/check** from the file's directory. Where it says skip, or a build directory would have to be created first, skip.

If anything fails, stop and report. The version is still unchanged, so re-running after a fix is safe.

### 3. Update version in ALL detected files

1. Edit the version string in every version-bearing file, then apply each reference's **Extra update steps**. Touch no other field.
2. Run `versions.py verify --expect {NEW_VERSION}`. It re-detects every file, checks that JSON/TOML/XML/plist files still parse, and that each resolved version matches `MAJOR.MINOR.PATCH` of the new version.
3. If `passed` is false, fix the files named in `checks` and return to 2. Entries with `manual: true` are indirections the script cannot follow; confirm those by reading the file.

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

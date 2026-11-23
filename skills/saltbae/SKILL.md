---
name: saltbae
description: Carve uncommitted changes into properly-sized logical commits, using planning docs (plan files, CLAUDE.md, README, implementation plans) as grounds for grouping, and season each with a clear commit message. With the `bump` argument, additionally bump the project version, build, commit and tag — auto-detects the version-bearing file(s) across a broad range of language ecosystems (npm/Node, Cargo/Rust, Python, Java/Kotlin/Scala, Go, Ruby, PHP, C/C++, C#/.NET, Swift/Objective-C, Dart/Flutter, PowerShell, and more), starting with package.json / Cargo.toml / tauri.conf.json / pyproject.toml / CMakeLists.txt — and syncs matching version references in other files (README, install scripts, etc.). Use when the user wants to organize/split/commit working-tree changes, or cut a version bump / release tag.
argument-hint: bump | x.x.x
---

# Saltbae — carve changes into well-seasoned commits

## Input

Arguments: $ARGUMENTS

- Empty → **default mode**: carve uncommitted changes into commits and season each with a clear commit message (Part 1 only).
- `bump` or `bump <version>` → **bump mode**: run default mode first, then run the version bump flow (Part 1 + Part 2). If `<version>` is given (e.g. `v4.2.1` or `4.2.1`), strip the leading `v` and use it; otherwise auto-increment the patch number.

## Absolute rule — no AI attribution

Every commit created by this skill must NEVER contain any string suggesting AI involvement — no `Co-Authored-By: Claude ...`, no `Generated with Claude Code`, no mention of Anthropic/Claude/AI in any form. Content of the change only. This overrides any default behavior that appends such trailers.

## Part 1 — Carve & Season

### 1. Check working tree

Run `git status`. If the working tree is clean: in default mode, report "nothing to carve" and stop; in bump mode, continue to Part 2.

### 2. Gather grouping evidence

Determine what each change belongs to, in this priority order:

**a. Dedicated planning directory? (check first)**
If a planning directory exists in the repo root (e.g. `.planning/`, `plans/`, `docs/plans/`), read what is relevant: state/status files, current phase or plan files (`PLAN*.md`, `SUMMARY*.md`), and roadmap files if the context is unclear.

Use these to map changes to phases/plans/tasks.

**b. Other planning docs (fallback / supplement)**
If no planning directory, or it doesn't explain the changes, look for other design/implementation grounds (check existence before reading; read only what plausibly relates to the diff):
- `CLAUDE.md`, `AGENTS.md`
- `README.md`
- Common plan files: `IMPLEMENTATION_PLAN*.md`, `PLAN*.md`, `PLANNING*.md`, `TODO*.md`, `ROADMAP*.md`, `docs/` design docs
- Open PR/issue references in branch name (e.g. `fix/issue-123`)

**c. Always available**
- Current conversation context — what work was actually done this session
- `git log --oneline -15` — recent commit message style and granularity conventions
- The diffs themselves (`git diff`, `git diff --stat`) — cohesion by feature/module

### 3. Group and split

- Group related changes into logical units. Changes spanning multiple features/fixes → separate commits.
- A commit should be one reviewable unit: a feature, a fix, a refactor, a docs update — not a mixture.
- Split so that each commit maps to exactly ONE release-note category (see Part 2 step 8): Added / Changed / Fixed / Removed / Performance / Documentation / Security. A change that both adds a feature and fixes a bug → two commits.
  - **Exception**: if splitting would leave an intermediate commit that doesn't build/type-check (e.g. the fix and the feature are entangled in the same function, or one depends on the other's type change), keep it as one commit and classify it later by its dominant purpose. Judge this by mentally tracing whether staging only one half would pass step 2-style build/checks — don't actually run builds per split candidate.
- Test files belong with the code they test.
- Match the repository's existing commit message style (prefix conventions like `feat:`/`fix:`, language, phase notation, etc.) observed in step 2c.
- Follow any commit rules in the project's CLAUDE.md strictly.

### 4. Commit

Stage and commit each group in order. Use `git add <specific paths>` — never `git add -A` when splitting.

**Splitting within a file — stage hunks, keep the working tree untouched.** When one file contains changes belonging to different commits, do everything at the index level, the way a human uses `git add -p`: extract only the relevant hunks into a patch and stage them with `git apply --cached <patch>` (patch files go in the scratchpad), then commit. The working tree files stay exactly as they are throughout — every intermediate state exists only in the index. Temporary copies of source files, editing a file down to a partial state, or moving files aside all stay off the table; the index is the only splitting mechanism.

**Write the message like a human maintainer would, not a phase-completion report:**
- **Subject**: imperative mood, ≤50 chars where possible (72 is a hard ceiling), no trailing period — the *what*, at a glance.
- **Body** (only if the subject doesn't already cover the *why*): blank line, then wrapped ~72 cols. State what changed and why it was needed. Never narrate *how* step-by-step, and never re-derive detail the diff already shows. A handful of bullets is normal; past ~15 lines you have drifted into writing a report, not a commit — cut it back to the essential why.
- Leave out of the message entirely: verification transcripts (test/build output, pass/fail counts, command invocations), exhaustive file-by-file listings (`git show --stat` recovers this on demand), edge-case-by-edge-case narration, and deferred-work rationale — none of it survives usefully in `git log`. If the project keeps plan/summary files, that detail already belongs there — reference it (`see SUMMARY.md`) instead of re-narrating it in the commit body.
- Matching the repo's existing style (prefix conventions, language) from step 2c is about *form*, not license to expand length or content beyond the rules above.

### 5. Report

Print a short summary: commits created (hash, message, files) and anything intentionally left uncommitted (with reason).

In default mode, stop here. In bump mode, continue.

## Part 2 — Bump (only in bump mode)

Follow strictly in order. Stop immediately if any step fails.

### 1. Detect version files and current version

Search the repo for the detection patterns below, at the root and in subdirectories, excluding `.git/` and dependency/build-output directories (`node_modules/`, `target/`, `dist/`, `build/`). For each pattern found, read the matching file under `references/ecosystems/`, and only those. Each reference defines, per tool: detection, version-bearing file and field, bump-rule nuance, build/check, lockfile, and extra update steps.

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

Run `git grep -nF` for the OLD version string across tracked files — search BOTH the bare form (e.g. `0.1.0`) and the `v`-prefixed tag form (e.g. `v0.1.0`), since references may use either. For each match outside the files already updated in step 3, use judgment: update genuine version pins (README install one-liners/badges, install-script pinned refs or tags, CDN URLs embedding the version). Do NOT touch historical records (CHANGELOG entries, past release notes) or lockfiles (handled in the next step). If a match is ambiguous, stop and ask the user.

### 5. Update lockfiles

For each tool whose files were updated in step 3, run the procedure in its reference's **Lockfile** section from the file's directory.

### 6. Commit

Stage ONLY the version files from step 3, the reference files from step 4, and the lockfiles from step 5. Commit message:

```
chore: bump version to {VERSION}
```

### 7. Tag

```
git tag -a v{VERSION} -m "v{VERSION}"
```

### 8. Generate release notes

For pasting into the GitHub Releases text field when publishing this tag — this is manual copy-paste, not something the skill posts anywhere, so just print it as part of step 9's output.

- Range: `PREV_TAG..HEAD` (from step 1), excluding this bump commit itself — its `chore: bump version to {VERSION}` message is boilerplate, not a release note. If there's no `PREV_TAG` (first release), cover full history instead and label it "Initial release".
- `git log PREV_TAG..HEAD --oneline` lists the raw candidates. Each bullet is the commit's subject line, verbatim or lightly smoothed — one line per commit, never expanded with body detail. Merge commits into a single bullet when they're trivially the same logical change (e.g. a fix immediately following what it fixes).
- Classify each commit into exactly ONE category — never list the same commit under two headers:
  - Categories, in output order: `## Added` / `## Changed` / `## Fixed` / `## Removed` / `## Performance` / `## Documentation` / `## Security`.
  - Judge by: ① message prefix if present (`feat:`→Added, `fix:`→Fixed, `perf:`→Performance, `docs:`→Documentation), ② otherwise the dominant purpose from the subject and diff.
  - Tie-break for ambiguous commits: Security > Fixed > Added > Removed > Performance > Documentation > Changed (Changed is the catch-all for refactors and behavior changes).
  - Exclude pure maintenance commits (version bumps, CI config, lockfile-only) from the notes entirely.
- Omit any category with zero commits — no empty headers.
- Output as plain Markdown, ready to paste as-is — no surrounding commentary.

### 9. Done

Print a summary:
- Old version → new version
- Files updated
- Commit hash (short) and tag name
- The release notes from step 8, clearly delimited (e.g. a fenced block) so they're easy to copy into GitHub's release notes text field for this tag
- Remind the user to `git push && git push --tags` when ready.

---
name: saltbae
description: Sift uncommitted changes into properly-sized logical commits, using GSD (.planning/) or other planning docs (CLAUDE.md, README, implementation plans) as grounds for grouping. With the `bump` argument, additionally bump the project version, build, commit and tag — auto-detects the version-bearing file(s) across a broad range of language ecosystems (npm/Node, Cargo/Rust, Python, Java/Kotlin/Scala, Go, Ruby, PHP, C/C++, C#/.NET, Swift/Objective-C, Dart/Flutter, PowerShell, and more), starting with package.json / Cargo.toml / tauri.conf.json / pyproject.toml / CMakeLists.txt — and syncs matching version references in other files (README, install scripts, etc.). Use when the user wants to organize/split/commit working-tree changes, or cut a version bump / release tag.
argument-hint: bump | x.x.x
---

# Saltbae — sift changes into well-seasoned commits

## Input

Arguments: $ARGUMENTS

- Empty → **sift mode**: organize uncommitted changes into commits (Part 1 only).
- `bump` or `bump <version>` → **bump mode**: sift first, then run the version bump flow (Part 1 + Part 2). If `<version>` is given (e.g. `v4.2.1` or `4.2.1`), strip the leading `v` and use it; otherwise auto-increment the patch number.

## Absolute rule — no AI attribution

Every commit created by this skill must NEVER contain any string suggesting AI involvement — no `Co-Authored-By: Claude ...`, no `Generated with Claude Code`, no mention of Anthropic/Claude/AI in any form. Content of the change only. This overrides any default behavior that appends such trailers.

## Part 1 — Sift

### 1. Check working tree

Run `git status`. If the working tree is clean: in sift mode, report "nothing to sift" and stop; in bump mode, continue to Part 2.

### 2. Gather grouping evidence

Determine what each change belongs to, in this priority order:

**a. GSD project? (check first)**
If `.planning/` exists in the repo root, this is a GSD-managed project. Read what is relevant:
- `.planning/STATE.md` — current phase and position
- Current phase directory (`.planning/phases/<current>/`) — `PLAN*.md`, `SUMMARY*.md`
- `.planning/ROADMAP.md` — if phase context is unclear

Use these to map changes to phases/plans/tasks.

**b. Non-GSD planning docs (fallback / supplement)**
If no `.planning/`, or it doesn't explain the changes, look for other design/implementation grounds (check existence before reading; read only what plausibly relates to the diff):
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
- Leave out of the message entirely: verification transcripts (test/build output, pass/fail counts, command invocations), exhaustive file-by-file listings (`git show --stat` recovers this on demand), edge-case-by-edge-case narration, and deferred-work rationale — none of it survives usefully in `git log`. If the project is GSD-managed, that detail already belongs in `.planning/phases/<phase>/SUMMARY*.md` or its PROGRESS csv/log — reference it (`see SUMMARY.md`) instead of re-narrating it in the commit body.
- Matching the repo's existing style (prefix conventions, language) from step 2c is about *form*, not license to expand length or content beyond the rules above.

### 5. Report

Print a short summary: commits created (hash, message, files) and anything intentionally left uncommitted (with reason).

In sift mode, stop here. In bump mode, continue.

## Part 2 — Bump (only in bump mode)

Follow strictly in order. Stop immediately if any step fails.

### 1. Detect version files and current version

Search the repo for version-bearing files, excluding `node_modules/`, `target/`, `dist/`, `build/`, `.git/`:

- `package.json` — `"version"` field. In a monorepo/workspace, which package(s) to bump is itself deterministic by file existence: `lerna.json` present → use its `"version"` key (a literal semver string means fixed/locked mode — all packages share one version line; the literal string `"independent"` means each package's own `package.json` version is bumped separately) → else `nx.json` with a `release` block present → follow Nx Release's versioning semantics → else a `.changeset/` directory present → the Changesets flow (`pnpm changeset version` / `yarn changeset version` / `npx changeset version` writes the new version into each affected package's `package.json`) → else a `workspaces` field in the root `package.json` (or a `pnpm-workspace.yaml`) with none of the above tooling → bump each workspace package's own `package.json` version independently → else a single-package repo → bump the root `package.json` version only (existing behavior, unchanged).
- `Cargo.toml` — `version` in `[package]`, OR `version` in `[workspace.package]` when the file has a `[workspace]` section (a "virtual manifest" — one with `[workspace]` but no `[package]` — is still version-bearing if `[workspace.package].version` is present). Member crates that declare `version.workspace = true` inherit the root version automatically at parse time — do not edit them; only a member with its own literal `version = "x.y.z"` is independently versioned. Only skip a `Cargo.toml` entirely when it has `[workspace]` and neither `[package].version` nor `[workspace.package].version` is present.
- `tauri.conf.json` — `"version"` field
- `pyproject.toml` — priority order: `[project].version` (a literal key, not listed under `dynamic`) → else `[tool.poetry].version` → else `[tool.setuptools.dynamic].version`'s `attr:`/`file:` indirection (edit the module attribute or file it points to, not `pyproject.toml` itself) → else `dynamic = ["version"]` with `setuptools_scm`/`hatch-vcs`/`versioneer` in `[build-system].requires` (no file exists for this case — it's handled entirely by the git-tag fallback below, not a gap) → else `setup.cfg`'s `[metadata].version` (literal, or its own `attr:`/`file:` indirection) → else `setup.py`'s `setup(version=...)` kwarg (if the value isn't a quoted string literal, trace the variable/expression to whichever file actually defines it — commonly a `_version.py`/`__init__.py` module attribute — and treat that file as version-bearing instead) → else the git-tag fallback below.
- `CMakeLists.txt` — `VERSION` in the top-level `project(... VERSION x.y.z ...)` call
- Every other supported ecosystem (PHP, Ruby, Java/Kotlin, Scala, Go, Shell, C/C++ beyond CMake, C#/.NET, Swift/Objective-C, Dart/Flutter, PowerShell, and bonus Haskell/Elixir/Lua) — see `references/version-ecosystems.md` for the detection signal, version-bearing file(s)/field, and bump-rule nuance of each.

They may live in subdirectories (e.g. `rust/package.json`). List every file found — ALL of them will be updated in sync, including across different ecosystems coexisting in one repo (e.g. a Tauri app has `package.json` + `Cargo.toml` + `tauri.conf.json` all in sync; a C++ project may have `CMakeLists.txt` alongside `vcpkg.json`).

- **Consensus rule**: if all detected files/build-systems agree on the current version, use it. If they disagree — including within a single language, e.g. a C++ repo mid-migration with both `CMakeLists.txt` and `meson.build` — stop and ask the user which is canonical. Never silently prefer one file/build-system over another via a fixed priority order; a strict override risks updating the wrong file during a migration.
- If no version-bearing manifest file is found at all, derive the current version from the latest git tag: `git describe --tags --abbrev=0` (strip a leading `v` for the numeric version). For ecosystems with no version-file concept by design — Go modules, Shell scripts with no `package.json`, and pure SwiftPM packages (`Package.swift`) — this git-tag read is the correct **primary** mechanism, not a fallback of last resort; treat it as expected, not as a gap. If there is also no tag, stop and ask the user for the current version.
- Compute the new version. **Patch increment is purely numeric** — `0.4.9` → `0.4.10`, NOT `0.5.0`. MINOR and MAJOR never change on auto-increment.
- **Suffix/prerelease preservation**: only apply the auto-increment above when the detected version is a bare `MAJOR.MINOR.PATCH` with no suffix. When a suffix marker is present — a semver prerelease/build-metadata tag (`-beta.1`, `+build5`), a PEP 440 pre/post/dev/local segment (`1.2.0rc1`, `1.2.0.post1`, `1.2.0.dev0`, `1.2.0+local`), or a RubyGems `.pre`/`.rc` marker — stop and ask the user what the intended next version is, instead of incrementing through it. **Exception: Maven/sbt's `-SNAPSHOT` suffix** is a perpetual in-development marker, not a specific-prerelease choice — auto-increment the numeric part as usual and preserve `-SNAPSHOT` unchanged (e.g. `1.2.3-SNAPSHOT` → `1.2.4-SNAPSHOT`); only strip it when the bump is explicitly a release cut.
- Validate semver format (MAJOR.MINOR.PATCH). Print the transition (e.g., `0.3.14 → 0.3.15`).
- Record `PREV_TAG` for step 8's release notes: the tag `v{OLD_VERSION}`, if it exists (`git rev-parse -q --verify v{OLD_VERSION}`). If it doesn't exist, this is the first release — there is no `PREV_TAG`, and step 8 covers full history instead.

### 2. Build / check (before version update)

Run what the detected toolchains provide, from each file's directory:

- `package.json` with a `build` script → `npm run build` (or the lockfile-matching package manager: pnpm/yarn/bun). If `tsconfig.json` is present (same ecosystem, not a separate branch): additionally run `tsc --noEmit` (or the project's own `scripts.typecheck`/`scripts.type-check` entry if defined) as a build-independent type-check.
- `Cargo.toml` → `cargo check`, or `cargo check --workspace` whenever the file has a `[workspace]` section (plain `cargo check` on a non-virtual workspace silently checks only the root crate and skips other members)
- `pyproject.toml` with configured checks (e.g. `ruff`, `pytest` if present) → run them; also run `python -m build --sdist --wheel .` as the build-sanity step (this ecosystem otherwise only lints/tests, unlike the Cargo/npm rows which build) — if no build backend is configured either, skip
- `CMakeLists.txt` → `cmake --build <builddir>` if a build directory already exists from prior development; otherwise skip (matching the pyproject.toml precedent — this step never bootstraps a project from scratch)
- Every other supported ecosystem — see `references/version-ecosystems.md`'s build/check entry for the exact command, or its explicit "skip, no reliable command" note where one isn't confirmed

If anything fails, stop and report. The version has not been changed yet, so re-running after a fix is safe.

### 3. Update version in ALL detected files

Use the Edit tool to update the version string in every file found in step 1. Do NOT touch any other fields.

### 4. Update other version references

Run `git grep -nF` for the OLD version string across tracked files — search BOTH the bare form (e.g. `0.1.0`) and the `v`-prefixed tag form (e.g. `v0.1.0`), since references may use either. For each match outside the files already updated in step 3, use judgment: update genuine version pins (README install one-liners/badges, install-script pinned refs or tags, CDN URLs embedding the version). Do NOT touch historical records (CHANGELOG entries, past release notes) or lockfiles (handled in the next step). If a match is ambiguous, stop and ask the user.

### 5. Update lockfiles

- `Cargo.toml` updated → run `cargo check` from its directory so `Cargo.lock` picks up the new version (fast; cache is warm from step 2).
- `package.json` updated → regenerate whichever lockfile is present, determined by file existence: `pnpm-lock.yaml` present → pnpm → `pnpm install --lockfile-only`; else `yarn.lock` present → yarn → `yarn install --mode=update-lockfile`; else `package-lock.json` present (or no lockfile yet) → npm → `npm install --package-lock-only`. Each of these updates only the lockfile, not `node_modules`.

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

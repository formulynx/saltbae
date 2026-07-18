---
name: saltbae
description: Sift uncommitted changes into properly-sized logical commits, using GSD (.planning/) or other planning docs (CLAUDE.md, README, implementation plans) as grounds for grouping. With the `bump` argument, additionally bump the project version, build, commit and tag (auto-detects package.json / Cargo.toml / tauri.conf.json / pyproject.toml / CMakeLists.txt), and syncs matching version references in other files (README, install scripts, etc.). Use when the user wants to organize/split/commit working-tree changes, or cut a version bump / release tag.
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
- Test files belong with the code they test.
- Match the repository's existing commit message style (prefix conventions like `feat:`/`fix:`, language, phase notation, etc.) observed in step 2c.
- Follow any commit rules in the project's CLAUDE.md strictly.

### 4. Commit

Stage and commit each group in order. Use `git add <specific paths>` — never `git add -A` when splitting.

### 5. Report

Print a short summary: commits created (hash, message, files) and anything intentionally left uncommitted (with reason).

In sift mode, stop here. In bump mode, continue.

## Part 2 — Bump (only in bump mode)

Follow strictly in order. Stop immediately if any step fails.

### 1. Detect version files and current version

Search the repo for version-bearing files, excluding `node_modules/`, `target/`, `dist/`, `build/`, `.git/`:

- `package.json` — `"version"` field
- `Cargo.toml` — `version` in `[package]` (skip workspace-only manifests)
- `tauri.conf.json` — `"version"` field
- `pyproject.toml` — `version` in `[project]` or `[tool.poetry]`
- `CMakeLists.txt` — `VERSION` in the top-level `project(... VERSION x.y.z ...)` call

They may live in subdirectories (e.g. `rust/package.json`). List every file found — ALL of them will be updated in sync.

- If all files agree on the current version, use it. If they disagree, stop and ask the user which is canonical.
- If no version-bearing manifest file is found at all, derive the current version from the latest git tag: `git describe --tags --abbrev=0` (strip a leading `v` for the numeric version). If there is also no tag, stop and ask the user for the current version.
- Compute the new version. **Patch increment is purely numeric** — `0.4.9` → `0.4.10`, NOT `0.5.0`. MINOR and MAJOR never change on auto-increment.
- Validate semver format (MAJOR.MINOR.PATCH). Print the transition (e.g., `0.3.14 → 0.3.15`).

### 2. Build / check (before version update)

Run what the detected toolchains provide, from each file's directory:

- `package.json` with a `build` script → `npm run build` (or the lockfile-matching package manager: pnpm/yarn/bun)
- `Cargo.toml` → `cargo check`
- `pyproject.toml` with configured checks (e.g. `ruff`, `pytest` if present) → run them; otherwise skip

If anything fails, stop and report. The version has not been changed yet, so re-running after a fix is safe.

### 3. Update version in ALL detected files

Use the Edit tool to update the version string in every file found in step 1. Do NOT touch any other fields.

### 4. Update other version references

Run `git grep -nF` for the OLD version string across tracked files — search BOTH the bare form (e.g. `0.1.0`) and the `v`-prefixed tag form (e.g. `v0.1.0`), since references may use either. For each match outside the files already updated in step 3, use judgment: update genuine version pins (README install one-liners/badges, install-script pinned refs or tags, CDN URLs embedding the version). Do NOT touch historical records (CHANGELOG entries, past release notes) or lockfiles (handled in the next step). If a match is ambiguous, stop and ask the user.

### 5. Update lockfiles

- `Cargo.toml` updated → run `cargo check` from its directory so `Cargo.lock` picks up the new version (fast; cache is warm from step 2).
- `package.json` updated and a lockfile references the root package version → run the package manager's install/lockfile-only command if needed.

### 6. Commit

Stage ONLY the version files from step 3, the reference files from step 4, and the lockfiles from step 5. Commit message:

```
chore: bump version to {VERSION}
```

### 7. Tag

```
git tag -a v{VERSION} -m "v{VERSION}"
```

### 8. Done

Print a summary:
- Old version → new version
- Files updated
- Commit hash (short) and tag name
- Remind the user to `git push && git push --tags` when ready.

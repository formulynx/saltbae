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
- Record `PREV_TAG` for step 8's release notes: the tag `v{OLD_VERSION}`, if it exists (`git rev-parse -q --verify v{OLD_VERSION}`). If it doesn't exist, this is the first release — there is no `PREV_TAG`, and step 8 covers full history instead.

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

### 8. Generate release notes

For pasting into the GitHub Releases text field when publishing this tag — this is manual copy-paste, not something the skill posts anywhere, so just print it as part of step 9's output.

- Range: `PREV_TAG..HEAD` (from step 1), excluding this bump commit itself — its `chore: bump version to {VERSION}` message is boilerplate, not a release note. If there's no `PREV_TAG` (first release), cover full history instead and label it "Initial release".
- `git log PREV_TAG..HEAD --oneline` lists the raw candidates. For each, read the subject (and body when the subject alone doesn't convey the user-facing effect) and write ONE concise bullet describing what changed — same what/why spirit as step 4's commit-message rules: no *how*, no verification-transcript detail. Merge commits into a single bullet when they're trivially the same logical change (e.g. a fix immediately following what it fixes).
- Group under `### Features` / `### Fixes` / `### Docs` etc. only if the repo's own commits consistently use matching prefixes (step 2c already established this); otherwise a flat bullet list.
- Output as plain Markdown (`- ...`), ready to paste as-is — no surrounding commentary.

### 9. Done

Print a summary:
- Old version → new version
- Files updated
- Commit hash (short) and tag name
- The release notes from step 8, clearly delimited (e.g. a fenced block) so they're easy to copy into GitHub's release notes text field for this tag
- Remind the user to `git push && git push --tags` when ready.

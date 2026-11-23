# JavaScript / TypeScript

## npm (and pnpm / yarn / bun)

### Detection

`package.json` at the repo root or in a subdirectory (e.g. `rust/package.json`).

### Version-bearing file

`package.json`'s `"version"` field.

In a monorepo/workspace, which package(s) to bump is determined by file existence, in this order:

1. `lerna.json` present → use its `"version"` key.
   - A literal semver string means fixed/locked mode. All packages share one version line.
   - The literal string `"independent"` means each package's own `package.json` version is bumped separately.
2. Else `nx.json` with a `release` block present → follow Nx Release's versioning semantics.
3. Else a `.changeset/` directory present → the Changesets flow. `pnpm changeset version` / `yarn changeset version` / `npx changeset version` writes the new version into each affected package's `package.json`.
4. Else a `workspaces` field in the root `package.json`, or a `pnpm-workspace.yaml`, with none of the above tooling → bump each workspace package's own `package.json` version independently.
5. Else a single-package repo → bump the root `package.json` version only.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

- A `build` script present → `npm run build`, or the lockfile-matching package manager (pnpm/yarn/bun).
- `tsconfig.json` present → additionally run `tsc --noEmit` as a build-independent type-check. Use the project's own `scripts.typecheck` / `scripts.type-check` entry instead if defined.

### Lockfile

Regenerate whichever lockfile is present, determined by file existence. Each command updates only the lockfile, not `node_modules`.

1. `pnpm-lock.yaml` present → `pnpm install --lockfile-only`
2. Else `yarn.lock` present → `yarn install --mode=update-lockfile`
3. Else `package-lock.json` present, or no lockfile yet → `npm install --package-lock-only`

### Extra update steps

None.

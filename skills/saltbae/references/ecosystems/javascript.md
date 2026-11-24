# JavaScript / TypeScript

## npm (and pnpm / yarn / bun)

### Detection

`package.json`, at the root or in a subdirectory.

### Version-bearing file

`package.json`'s `"version"`. In a monorepo, decide which package(s) to bump by file existence, first match wins:

1. `lerna.json` → its `"version"`. A semver string means all packages share it; `"independent"` means each `package.json` is bumped separately.
2. `nx.json` with a `release` block → follow Nx Release.
3. `.changeset/` → run `<pm> changeset version`, which writes each affected `package.json`.
4. `workspaces` in the root `package.json`, or `pnpm-workspace.yaml` → bump each workspace `package.json` independently.
5. Otherwise → the root `package.json` only.

### Build/check

- `build` script present → `<pm> run build`, where `<pm>` matches the lockfile.
- `tsconfig.json` present → also `scripts.typecheck` / `scripts.type-check` if defined, else `tsc --noEmit`.

### Lockfile

First match wins; each command touches only the lockfile:

1. `pnpm-lock.yaml` → `pnpm install --lockfile-only`
2. `yarn.lock` → `yarn install --mode=update-lockfile`
3. `package-lock.json` or none → `npm install --package-lock-only`

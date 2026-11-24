# Claude Code plugin

## Plugin manifest / marketplace

### Detection

`.claude-plugin/plugin.json` or `.claude-plugin/marketplace.json`.

### Version-bearing file

(a) `"version"` in `.claude-plugin/plugin.json`. It takes precedence over a marketplace entry at install time.

(b) `"version"` on a `plugins[]` entry in `.claude-plugin/marketplace.json` → keep it in sync with (a), since `claude plugin validate` warns when they diverge.

(c) Neither set → nothing to edit. Installs track the source commit, so the release is the commit plus the tag.

The marketplace's own top-level `version` / `metadata.version` describe the marketplace manifest, not the plugin. Leave them alone unless the repo already keeps them in lockstep.

### Build/check

`claude plugin validate .` from the directory that holds `.claude-plugin/`.

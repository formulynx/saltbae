# saltbae

`saltbae` is a commit-hygiene skill for
[Claude Code](https://claude.com/product/claude-code). The `/saltbae`
command sifts your uncommitted working-tree changes into properly-sized,
logically-grouped commits, using GSD (`.planning/`) or other planning docs
(`CLAUDE.md`, `README.md`, implementation plans) as grounds for grouping.
With the `bump` argument, it additionally bumps the project's version,
runs the build/checks, updates the commit and tag, and syncs matching
version references in other files (README, install scripts, etc.).

This repo is distributed as a plain skill file, installed via a symlink —
there is no plugin manifest, so the command stays available as the bare
`/saltbae`.

## Why "saltbae"?

The name nods to the meme-famous steakhouse chef known online as "Salt
Bae" — celebrated for a dramatic tableside cut and a theatrical sprinkle of
salt from on high before serving. However good the meat, without a proper
cut (splitting the diff into logical commits) and deliberate seasoning (a
commit log that reads clearly) the diner can't really chew it — literally —
or taste it, i.e. review it. Cooking the meat itself (whether the code
works) is a different skill from plating it for the guest (whether the
change is legible to someone else): the programmer's job is the former,
`saltbae`'s is the latter — carving and seasoning the working tree into a
change history worth serving.

## Usage

Inside a Claude Code session, invoke:

```
/saltbae
```

**Sift mode** (no arguments): organizes your current uncommitted changes
into one or more logical commits.

```
/saltbae bump
/saltbae bump 4.2.1
```

**Bump mode**: sifts first, then bumps the project version (auto-incrementing
the patch number, or to the version given explicitly), runs the
build/checks, updates version references across the repo, commits, and tags
the release.

A notable behavior in both modes: commits created by this skill never
contain any AI-attribution string (no `Co-Authored-By: Claude ...`, no
"Generated with Claude Code", no mention of Anthropic/Claude/AI) — this rule
overrides any default trailer behavior.

## Install

Pick the installer for your shell:

- **macOS / Linux / WSL / Git Bash** (any POSIX shell) → `install.sh` (below).
- **Native Windows** (PowerShell or cmd, no POSIX shell) → `install.ps1`
  ([PowerShell install](#powershell-install-native-windows)).

On Git Bash, prefer `install.sh`'s curl | bash method — it *copies* the file,
whereas its git-clone method relies on symlinks (`ln -s`), which Git Bash does
not create reliably. WSL has no such caveat. `install.ps1` always copies.

### Quick install (curl | bash via jsDelivr)

```sh
curl -fsSL https://cdn.jsdelivr.net/gh/formulynx/saltbae@v0.1.4/install.sh | bash
```

This fetches `skills/saltbae/SKILL.md` from jsDelivr's GitHub CDN and copies
it into `~/.claude/skills/saltbae/SKILL.md`. No local clone is created.

Before piping a remote script into `bash`, it's good practice to inspect it
first: `curl -fsSL <same-url> -o install.sh && less install.sh && bash
install.sh`. The one-liner above is pinned to a released tag (`@v0.1.4`) so
installs stay reproducible — jsDelivr caches tags/commits effectively
forever. Each release updates this README to point at the new tag; if you
want the latest in-development code instead, substitute `@main` (a moving
ref, cached by jsDelivr for ~12h).

### git clone (for development / contributors)

```sh
git clone <repo-url> saltbae
saltbae/install.sh
```

This symlinks `skills/saltbae` from the clone into `~/.claude/skills/saltbae`.

If `~/.claude/skills/saltbae` already exists as a real file/directory (not a
symlink) — e.g. from a previous manual install — back it up or remove it
before running `install.sh`; it will refuse to overwrite a real file and
exit with an error. (This guard only applies to the clone/symlink method;
the curl|bash method copies files and overwrites its own prior copies
freely.)

You can install into a different Claude config directory by setting
`CLAUDE_DIR` before running the script, e.g. `CLAUDE_DIR=/path/to/dir
saltbae/install.sh`.

### PowerShell install (native Windows)

For native Windows without a POSIX shell, use the PowerShell installer. Quick
install:

```powershell
irm https://cdn.jsdelivr.net/gh/formulynx/saltbae@v0.1.4/install.ps1 | iex
```

Or from a git clone:

```powershell
.\saltbae\install.ps1
```

`install.ps1` mirrors `install.sh` — the same payload file into
`~\.claude\skills\saltbae\SKILL.md` — but always **copies** (no symlinks;
those need admin/Developer Mode on Windows). It's idempotent and honours the
same `CLAUDE_DIR`, `SALTBAE_REF`, and `SALTBAE_BASE_URL` environment
variables. To inspect before running, download first: `irm <same-url>
-OutFile install.ps1; notepad install.ps1; .\install.ps1`.

If PowerShell blocks the script with an execution-policy error, run it for the
current process only: `powershell -ExecutionPolicy Bypass -File .\install.ps1`.

## Update

If you installed via curl | bash, re-running the same pinned one-liner just
reinstalls the same `v0.1.4` copy — it does not fetch newer code. To
upgrade, run the one-liner for the newer release tag (swap `@v0.1.4` for the
new tag), or use `@main` for the latest in-development version.

If you installed via git clone, pull the repo instead:

```sh
git -C saltbae pull
```

`SKILL.md` changes take effect immediately on the next `/saltbae`
invocation — no session restart needed, since there's no agent file to
reload (unlike xbb).

## Uninstall

```sh
saltbae/install.sh --uninstall
```

(or, if installed via curl | bash without keeping the script around, fetch
it again first: `curl -fsSL
https://cdn.jsdelivr.net/gh/formulynx/saltbae@v0.1.4/install.sh | bash -s --
--uninstall`). This works for both the symlink and copy install methods.

On native Windows, download `install.ps1` and run it with `-Uninstall`:

```powershell
irm https://cdn.jsdelivr.net/gh/formulynx/saltbae@v0.1.4/install.ps1 -OutFile install.ps1
.\install.ps1 -Uninstall
```

Alternatively, remove the skill manually (`~/.claude/skills/saltbae` is a
symlink if you installed via git clone, or a real directory if you installed
via curl | bash, hence `-rf`):

```sh
rm -rf ~/.claude/skills/saltbae
```

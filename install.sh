#!/usr/bin/env bash
# Installs the saltbae skill into a Claude Code config dir.
#
# Two modes:
#   - Clone mode: run from a local git clone (./install.sh) -> symlinks the
#     payload file from the repo into $CLAUDE_DIR.
#   - Remote mode: piped via curl|bash with no local clone -> fetches the
#     payload file from jsDelivr and copies it into $CLAUDE_DIR.
#
# Re-running is safe (idempotent). Supports --uninstall.
set -euo pipefail

OWNER=formulynx
REPO=saltbae
REF="${SALTBAE_REF:-v0.1.3}"
BASE_URL="${SALTBAE_BASE_URL:-https://cdn.jsdelivr.net/gh/$OWNER/$REPO@$REF}"

say() { echo "==> $*"; }

main() {
  local claude_dir="${CLAUDE_DIR:-$HOME/.claude}"
  local skills_dir="$claude_dir/skills"
  local skill_link="$skills_dir/saltbae"

  if [ "${1:-}" = "--uninstall" ]; then
    say "Removing $skill_link"
    if [ -L "$skill_link" ]; then
      rm -f "$skill_link"
    else
      rm -f "$skill_link/SKILL.md" "$skill_link/.saltbae-ref" 2>/dev/null || true
      rmdir "$skill_link" 2>/dev/null || true
    fi
    echo "saltbae uninstalled."
    return
  fi

  # Clone mode only when invoked as a real script file. When piped
  # (curl|bash / `bash < install.sh`), BASH_SOURCE is unset — force remote mode
  # rather than letting dirname "" collapse to the current directory.
  local repo_dir=""
  if [ -f "${BASH_SOURCE[0]:-}" ]; then
    repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  fi

  say "Target: $skill_link"
  mkdir -p "$skills_dir"

  if [ -n "$repo_dir" ] && [ -f "$repo_dir/skills/saltbae/SKILL.md" ]; then
    # Clone mode: symlink from the local repo. Preserve existing guards.
    say "Installing saltbae $REF"
    say "Mode: local clone ($repo_dir) — symlinking"
    if [ -e "$skill_link" ] && [ ! -L "$skill_link" ]; then
      # A prior remote-mode install leaves a real dir containing just our
      # own SKILL.md (plus the .saltbae-ref version marker). Recognize and
      # replace it; refuse anything else.
      if [ -d "$skill_link" ] \
        && ! ls -A "$skill_link" 2>/dev/null | grep -qvx -e 'SKILL.md' -e '.saltbae-ref' \
        && grep -q '^name: saltbae$' "$skill_link/SKILL.md" 2>/dev/null; then
        rm -rf "$skill_link"
      else
        echo "Refusing to overwrite existing directory: $skill_link" >&2
        echo "Back it up or remove it, then re-run this installer." >&2
        exit 1
      fi
    fi

    ln -sfn "$repo_dir/skills/saltbae" "$skill_link"
  else
    # Remote mode: fetch the payload file and copy it into place.
    # A .saltbae-ref marker records the installed ref; skip if already current.
    # (Not written in clone mode — a symlink tracks the repo, no fixed version.)
    local ref_file="$skill_link/.saltbae-ref"
    local current=""
    if [ ! -L "$skill_link" ] && [ -f "$ref_file" ]; then
      current="$(cat "$ref_file")"
    fi
    if [ "$current" = "$REF" ]; then
      say "saltbae $REF is already installed — nothing to do."
      return
    fi
    if [ -n "$current" ]; then
      say "Updating saltbae from $current to $REF"
    else
      say "Installing saltbae $REF"
    fi
    say "Mode: remote — downloading from $BASE_URL"
    if ! command -v curl >/dev/null 2>&1; then
      echo "curl is required to install saltbae but was not found." >&2
      exit 1
    fi

    # A prior clone install may have left skill_link as a symlink; remove it
    # so we can create a real directory.
    if [ -L "$skill_link" ]; then
      rm -f "$skill_link"
    fi
    mkdir -p "$skill_link"

    say "Fetching skills/saltbae/SKILL.md"
    fetch "$BASE_URL/skills/saltbae/SKILL.md" "$skill_link/SKILL.md"
    echo "$REF" > "$ref_file"
  fi

  echo "saltbae $REF installed successfully. Restart Claude Code (or start a new session) to pick it up."
}

fetch() {
  local url="$1"
  local dest="$2"
  case "$url" in
    https://*)
      curl --proto '=https' --tlsv1.2 -fsSL "$url" -o "$dest"
      ;;
    *)
      curl -fsSL "$url" -o "$dest"
      ;;
  esac
}

main "$@"

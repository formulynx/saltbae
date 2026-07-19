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
REF="${SALTBAE_REF:-v0.1.2}"
BASE_URL="${SALTBAE_BASE_URL:-https://cdn.jsdelivr.net/gh/$OWNER/$REPO@$REF}"

main() {
  local claude_dir="${CLAUDE_DIR:-$HOME/.claude}"
  local skills_dir="$claude_dir/skills"
  local skill_link="$skills_dir/saltbae"

  if [ "${1:-}" = "--uninstall" ]; then
    if [ -L "$skill_link" ]; then
      rm -f "$skill_link"
    else
      rm -f "$skill_link/SKILL.md" 2>/dev/null || true
      rmdir "$skill_link" 2>/dev/null || true
    fi
    echo "uninstalled"
    return
  fi

  # Clone mode only when invoked as a real script file. When piped
  # (curl|bash / `bash < install.sh`), BASH_SOURCE is unset — force remote mode
  # rather than letting dirname "" collapse to the current directory.
  local repo_dir=""
  if [ -f "${BASH_SOURCE[0]:-}" ]; then
    repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  fi

  mkdir -p "$skills_dir"

  if [ -n "$repo_dir" ] && [ -f "$repo_dir/skills/saltbae/SKILL.md" ]; then
    # Clone mode: symlink from the local repo. Preserve existing guards.
    if [ -e "$skill_link" ] && [ ! -L "$skill_link" ]; then
      # A prior remote-mode install leaves a real dir containing just our
      # own SKILL.md. Recognize and replace it; refuse anything else.
      if [ -d "$skill_link" ] && [ "$(ls -A "$skill_link" 2>/dev/null)" = "SKILL.md" ] \
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

    fetch "$BASE_URL/skills/saltbae/SKILL.md" "$skill_link/SKILL.md"
  fi

  echo "installed"
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

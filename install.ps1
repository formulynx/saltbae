# Installs the saltbae skill into a Claude Code config dir (Windows / PowerShell).
#
# The PowerShell twin of install.sh, for native Windows where no POSIX shell
# (WSL / Git Bash) is in play. Two modes:
#   - Clone mode: run from a local git clone (.\install.ps1) -> copies the
#     payload file from the repo into $CLAUDE_DIR.
#   - Remote mode: piped via `irm <url> | iex` with no local clone -> fetches
#     the payload file from jsDelivr and copies it into $CLAUDE_DIR.
#
# On Windows this always COPIES (never symlinks): ln-style symlinks need admin
# or Developer Mode and are unreliable, so copy is the safe default - unlike
# install.sh's clone mode, there is no symlink variant here.
# Re-running is safe (idempotent). Uninstall: download this script, then run
# `.\install.ps1 -Uninstall`.

[CmdletBinding()]
param([switch]$Uninstall)

$ErrorActionPreference = 'Stop'

$Owner   = 'formulynx'
$Repo    = 'saltbae'
$Ref     = if ($env:SALTBAE_REF)      { $env:SALTBAE_REF }      else { 'v0.1.1' }
$BaseUrl = if ($env:SALTBAE_BASE_URL) { $env:SALTBAE_BASE_URL } else { "https://cdn.jsdelivr.net/gh/$Owner/$Repo@$Ref" }

$ClaudeDir = if ($env:CLAUDE_DIR) { $env:CLAUDE_DIR } else { Join-Path $HOME '.claude' }
$SkillsDir = Join-Path $ClaudeDir 'skills'
$SkillDir  = Join-Path $SkillsDir 'saltbae'

# Payload: repo-relative source path -> destination path.
# Keep in sync with install.sh's srcs/dests.
$Payload = @(
  @{ Src = 'skills/saltbae/SKILL.md'; Dest = (Join-Path $SkillDir 'SKILL.md') }
)

if ($Uninstall) {
  foreach ($p in $Payload) { Remove-Item -Force -ErrorAction SilentlyContinue $p.Dest }
  if ((Test-Path $SkillDir) -and -not (Get-ChildItem -Force $SkillDir)) {
    Remove-Item -Force $SkillDir
  }
  Write-Output 'uninstalled'
  return
}

New-Item -ItemType Directory -Force -Path $SkillsDir, $SkillDir | Out-Null

# Clone mode when run from a checkout that actually contains the payload;
# otherwise (e.g. `irm ... | iex`, where $PSScriptRoot is empty) remote mode.
$RepoDir = $PSScriptRoot
$LocalSkill = if ($RepoDir) { Join-Path $RepoDir 'skills/saltbae/SKILL.md' } else { $null }

if ($RepoDir -and (Test-Path $LocalSkill)) {
  foreach ($p in $Payload) {
    Copy-Item -Force -Path (Join-Path $RepoDir $p.Src) -Destination $p.Dest
  }
} else {
  # TLS 1.2 for Windows PowerShell 5.1, whose default may be too old for the CDN.
  [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
  foreach ($p in $Payload) {
    Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/$($p.Src)" -OutFile $p.Dest
  }
}

Write-Output 'installed'

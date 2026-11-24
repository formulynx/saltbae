#!/usr/bin/env python3
"""Detect, check tools for, and verify version-bearing files for saltbae bump.

Subcommands (all print JSON to stdout):
  detect                 list version-bearing files and their current versions
  tools                  list the commands each detected ecosystem needs, and
                         whether they are on PATH
  verify --expect X.Y.Z  re-detect after a bump and check every resolved file
                         parses and carries the expected version

Exit codes: 0 = ok, 1 = verify failed, 2 = usage or environment error.
Requires Python 3.8+. TOML parse checks need 3.11+ (tomllib) and are reported
as skipped on older versions.
"""
from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

EXCLUDED_DIRS = {
    ".git", "node_modules", "target", "dist", "build", "bin", "obj", "vendor",
}
CORE_RE = re.compile(r"\d+\.\d+\.\d+")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def list_files(root: Path) -> list[Path]:
    """Tracked + untracked-but-not-ignored files, minus excluded dirs."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=root, check=True, capture_output=True,
        ).stdout.decode()
        names = [n for n in out.split("\0") if n]
    except (subprocess.CalledProcessError, FileNotFoundError):
        names = [
            os.path.relpath(os.path.join(d, f), root)
            for d, _, fs in os.walk(root) for f in fs
        ]
    files = []
    for n in sorted(set(names)):
        parts = Path(n).parts
        if any(p in EXCLUDED_DIRS for p in parts[:-1]):
            continue
        p = root / n
        if p.is_file():
            files.append(p)
    return files


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def entry(root, path, ecosystem, tool, field, version=None, status="ok", note=None):
    return {
        "path": rel(path, root), "ecosystem": ecosystem, "tool": tool,
        "reference": f"references/ecosystems/{ecosystem}.md", "field": field,
        "version": version, "status": status, "note": note,
    }


def regex_entry(root, path, ecosystem, tool, field, pattern, flags=re.M):
    m = re.search(pattern, read(path), flags)
    if m:
        return entry(root, path, ecosystem, tool, field, m.group(1).strip())
    return None


# --- per-ecosystem extractors -------------------------------------------
# Each returns a list of entries. status values:
#   ok            literal version found
#   unresolved    version lives behind an indirection the reference explains
#   tag-versioned no version file by design; the git tag is the source
#   inconsistent  the same file holds conflicting values


def x_package_json(root, p):
    try:
        data = json.loads(read(p))
    except json.JSONDecodeError as e:
        return [entry(root, p, "javascript", "npm", "version", status="unresolved",
                      note=f"invalid JSON: {e}")]
    if isinstance(data.get("version"), str):
        return [entry(root, p, "javascript", "npm", '"version"', data["version"])]
    return []


def x_lerna(root, p):
    v = json.loads(read(p)).get("version")
    if v == "independent":
        return [entry(root, p, "javascript", "lerna", '"version"', status="unresolved",
                      note="independent mode: each package.json is versioned separately")]
    return [entry(root, p, "javascript", "lerna", '"version"', v)] if v else []


def x_cargo(root, p):
    text = read(p)
    if tomllib:
        d = tomllib.loads(text)
        pkg_v = d.get("package", {}).get("version")
        ws_v = d.get("workspace", {}).get("package", {}).get("version")
        if isinstance(pkg_v, str):
            return [entry(root, p, "rust", "cargo", "[package].version", pkg_v)]
        if isinstance(ws_v, str):
            return [entry(root, p, "rust", "cargo", "[workspace.package].version", ws_v)]
        return []  # inherits via version.workspace = true, or no version
    m = re.search(r'^\[(workspace\.package|package)\][^\[]*?^version\s*=\s*"([^"]+)"',
                  text, re.M | re.S)
    if m:
        return [entry(root, p, "rust", "cargo", f"[{m.group(1)}].version", m.group(2))]
    return []


def x_tauri(root, p):
    d = json.loads(read(p))
    v = d.get("version") or d.get("package", {}).get("version")
    if not isinstance(v, str):
        return []
    if v.endswith(".json"):
        return [entry(root, p, "rust", "tauri", '"version"', status="unresolved",
                      note=f"points to {v}; that file carries the version")]
    return [entry(root, p, "rust", "tauri", '"version"', v)]


def x_pyproject(root, p):
    text = read(p)
    if tomllib:
        d = tomllib.loads(text)
        proj = d.get("project", {})
        if isinstance(proj.get("version"), str) and "version" not in proj.get("dynamic", []):
            return [entry(root, p, "python", "pyproject", "[project].version", proj["version"])]
        poetry_v = d.get("tool", {}).get("poetry", {}).get("version")
        if isinstance(poetry_v, str):
            return [entry(root, p, "python", "poetry", "[tool.poetry].version", poetry_v)]
        if "version" in proj.get("dynamic", []):
            dyn = d.get("tool", {}).get("setuptools", {}).get("dynamic", {}).get("version")
            if dyn:
                return [entry(root, p, "python", "pyproject", "[tool.setuptools.dynamic].version",
                              status="unresolved", note=f"indirection: {dyn}")]
            reqs = " ".join(d.get("build-system", {}).get("requires", []))
            if re.search(r"setuptools[_-]scm|hatch-vcs|versioneer", reqs):
                return [entry(root, p, "python", "pyproject", "git tag", status="tag-versioned")]
            return [entry(root, p, "python", "pyproject", "dynamic version", status="unresolved")]
        return []
    m = re.search(r'^\[project\][^\[]*?^version\s*=\s*"([^"]+)"', text, re.M | re.S)
    if m:
        return [entry(root, p, "python", "pyproject", "[project].version", m.group(1))]
    return [entry(root, p, "python", "pyproject", "version", status="unresolved",
                  note="tomllib unavailable; resolve by reading the file")]


def x_setup_cfg(root, p):
    m = re.search(r"^\[metadata\][^\[]*?^version\s*=\s*(.+)$", read(p), re.M | re.S)
    if not m:
        return []
    v = m.group(1).strip()
    if v.startswith(("attr:", "file:")):
        return [entry(root, p, "python", "setup.cfg", "[metadata].version",
                      status="unresolved", note=f"indirection: {v}")]
    return [entry(root, p, "python", "setup.cfg", "[metadata].version", v)]


def x_setup_py(root, p):
    text = read(p)
    m = re.search(r"\bversion\s*=\s*['\"]([^'\"]+)['\"]", text)
    if m:
        return [entry(root, p, "python", "setup.py", "setup(version=...)", m.group(1))]
    if re.search(r"\bversion\s*=", text):
        return [entry(root, p, "python", "setup.py", "setup(version=...)", status="unresolved",
                      note="not a string literal; trace the expression")]
    return []


def x_cmake(root, p):
    m = re.search(r"\bproject\s*\([^)]*?\bVERSION\s+([^\s)]+)", read(p), re.I | re.S)
    return [entry(root, p, "c-cpp", "cmake", "project(VERSION)", m.group(1))] if m else []


def x_meson(root, p):
    m = re.search(r"\bproject\s*\((.*?)\)\s*$", read(p), re.S | re.M)
    if m:
        v = re.search(r"\bversion\s*:\s*'([^']+)'", m.group(1))
        if v:
            return [entry(root, p, "c-cpp", "meson", "project(version:)", v.group(1))]
    return []


def x_autoconf(root, p):
    return [e for e in [regex_entry(
        root, p, "c-cpp", "autotools", "AC_INIT 2nd argument",
        r"AC_INIT\(\s*\[?[^,\]]*\]?\s*,\s*\[?([^,\]\)]+)\]?")] if e]


def x_vcpkg(root, p):
    d = json.loads(read(p))
    for key in ("version", "version-semver", "version-date", "version-string"):
        if key in d:
            status = "ok" if key in ("version", "version-semver") else "unresolved"
            note = None if status == "ok" else f'"{key}" is not auto-bumped; ask the user'
            return [entry(root, p, "c-cpp", "vcpkg", f'"{key}"', d[key], status, note)]
    return []


def x_conan(root, p):
    text = read(p)
    m = re.search(r"^\s+version\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
    if m:
        return [entry(root, p, "c-cpp", "conan", "version attribute", m.group(1))]
    if "def set_version" in text:
        return [entry(root, p, "c-cpp", "conan", "set_version()", status="unresolved",
                      note="set_version() reads the version from another file")]
    return []


def x_composer(root, p):
    v = json.loads(read(p)).get("version")
    if isinstance(v, str):
        return [entry(root, p, "php", "composer", '"version"', v)]
    return [entry(root, p, "php", "composer", "git tag", status="tag-versioned")]


def x_gemspec(root, p):
    text = read(p)
    m = re.search(r"\.version\s*=\s*['\"]([^'\"]+)['\"]", text)
    if m:
        return [entry(root, p, "ruby", "rubygems", "spec.version", m.group(1))]
    found = []
    for vr in sorted((p.parent / "lib").glob("**/version.rb")):
        e = regex_entry(root, vr, "ruby", "rubygems", "VERSION constant",
                        r"VERSION\s*=\s*['\"]([^'\"]+)['\"]")
        if e:
            found.append(e)
    return found or [entry(root, p, "ruby", "rubygems", "spec.version", status="unresolved",
                           note="version constant not found under lib/")]


def x_gemfile(root, p):
    if list(p.parent.glob("*.gemspec")):
        return []
    return [entry(root, p, "ruby", "bundler", "git tag", status="tag-versioned")]


def x_pom(root, p):
    try:
        tree = ET.parse(p)
    except ET.ParseError as e:
        return [entry(root, p, "java-kotlin", "maven", "<version>", status="unresolved",
                      note=f"invalid XML: {e}")]
    r = tree.getroot()
    ns = r.tag[: r.tag.index("}") + 1] if r.tag.startswith("{") else ""
    v = r.find(f"{ns}version")
    if v is None or not (v.text or "").strip():
        return []  # inherits from <parent>
    text = v.text.strip()
    if "${revision}" in text:
        rev = r.find(f"{ns}properties/{ns}revision")
        if rev is not None and rev.text:
            return [entry(root, p, "java-kotlin", "maven", "<properties><revision>",
                          rev.text.strip())]
        return [entry(root, p, "java-kotlin", "maven", "${revision}", status="unresolved",
                      note="revision not in POM properties; check .mvn/maven.config")]
    return [entry(root, p, "java-kotlin", "maven", "/project/version", text)]


def x_gradle(root, p):
    props = p.parent / "gradle.properties"
    if props.is_file():
        e = regex_entry(root, props, "java-kotlin", "gradle", "version=",
                        r"^version\s*=\s*(\S+)")
        if e:
            return [e]
    if p.name.startswith("settings."):
        return []
    e = regex_entry(root, p, "java-kotlin", "gradle", "version =",
                    r"^\s*version\s*=\s*['\"]([^'\"]+)['\"]")
    return [e] if e else []


def x_sbt(root, p):
    vs = p.parent / "version.sbt"
    target = vs if vs.is_file() else p
    e = regex_entry(root, target, "scala", "sbt", "version :=",
                    r'version\s*:=\s*"([^"]+)"')
    return [e] if e else []


def x_gomod(root, p):
    return [entry(root, p, "go", "go", "git tag", status="tag-versioned")]


def x_msbuild(root, p):
    text = read(p)
    for tag in ("Version", "VersionPrefix"):
        m = re.search(rf"<{tag}>([^<]+)</{tag}>", text)
        if m:
            return [entry(root, p, "dotnet", "msbuild", f"<{tag}>", m.group(1).strip())]
    return []


def x_nuspec(root, p):
    e = regex_entry(root, p, "dotnet", "nuget", "<version>", r"<version>([^<]+)</version>")
    return [e] if e else []


def x_package_swift(root, p):
    return [entry(root, p, "swift-objc", "swiftpm", "git tag", status="tag-versioned")]


def x_podspec(root, p):
    e = regex_entry(root, p, "swift-objc", "cocoapods", "spec.version",
                    r"\.version\s*=\s*['\"]([^'\"]+)['\"]")
    return [e] if e else []


def x_pbxproj(root, p):
    vals = sorted(set(v.strip().strip('"') for v in
                      re.findall(r"MARKETING_VERSION\s*=\s*([^;]+);", read(p))))
    if not vals:
        return [entry(root, p, "swift-objc", "xcode", "MARKETING_VERSION", status="unresolved",
                      note="no MARKETING_VERSION; check Info.plist CFBundleShortVersionString")]
    if len(vals) > 1:
        return [entry(root, p, "swift-objc", "xcode", "MARKETING_VERSION",
                      ", ".join(vals), "inconsistent", "configurations disagree")]
    return [entry(root, p, "swift-objc", "xcode", "MARKETING_VERSION", vals[0])]


def x_pubspec(root, p):
    e = regex_entry(root, p, "dart", "pub", "version:", r"^version:\s*(\S+)")
    return [e] if e else []


def x_psd1(root, p):
    e = regex_entry(root, p, "powershell", "module", "ModuleVersion",
                    r"ModuleVersion\s*=\s*['\"]([^'\"]+)['\"]")
    return [e] if e else []


def x_cabal(root, p):
    e = regex_entry(root, p, "haskell", "cabal", "version:", r"^version:\s*(\S+)", re.M | re.I)
    return [e] if e else []


def x_hpack(root, p):
    e = regex_entry(root, p, "haskell", "hpack", "version:", r"^version:\s*(\S+)")
    return [e] if e else []


def x_mix(root, p):
    text = read(p)
    m = re.search(r'\bversion:\s*"([^"]+)"', text)
    if m:
        return [entry(root, p, "elixir", "mix", "version:", m.group(1))]
    m = re.search(r'@version\s+"([^"]+)"', text)
    if m:
        return [entry(root, p, "elixir", "mix", "@version", m.group(1))]
    return [entry(root, p, "elixir", "mix", "version:", status="unresolved",
                  note="not a literal; check for an external VERSION file")]


def x_rockspec(root, p):
    e = regex_entry(root, p, "lua", "luarocks", "version",
                    r"^version\s*=\s*['\"]([^'\"]+)['\"]")
    return [e] if e else []


def match(name: str, path: Path):
    """Return the extractor for a file, or None."""
    exact = {
        "package.json": x_package_json, "lerna.json": x_lerna,
        "Cargo.toml": x_cargo, "tauri.conf.json": x_tauri,
        "pyproject.toml": x_pyproject, "setup.cfg": x_setup_cfg, "setup.py": x_setup_py,
        "CMakeLists.txt": x_cmake, "meson.build": x_meson,
        "configure.ac": x_autoconf, "configure.in": x_autoconf,
        "vcpkg.json": x_vcpkg, "conanfile.py": x_conan,
        "composer.json": x_composer, "Gemfile": x_gemfile, "pom.xml": x_pom,
        "build.gradle": x_gradle, "build.gradle.kts": x_gradle,
        "settings.gradle": x_gradle, "settings.gradle.kts": x_gradle,
        "build.sbt": x_sbt, "go.mod": x_gomod,
        "Directory.Build.props": x_msbuild, "Package.swift": x_package_swift,
        "project.pbxproj": x_pbxproj, "pubspec.yaml": x_pubspec,
        "package.yaml": x_hpack, "mix.exs": x_mix,
    }
    if name in exact:
        if name == "project.pbxproj" and not path.parent.name.endswith(".xcodeproj"):
            return None
        return exact[name]
    suffix = {
        ".gemspec": x_gemspec, ".csproj": x_msbuild, ".fsproj": x_msbuild,
        ".vbproj": x_msbuild, ".nuspec": x_nuspec, ".podspec": x_podspec,
        ".psd1": x_psd1, ".cabal": x_cabal, ".rockspec": x_rockspec,
    }
    for ext, fn in suffix.items():
        if name.endswith(ext):
            return fn
    return None


def detect(root: Path) -> dict:
    files = list_files(root)
    entries, errors = [], []
    for p in files:
        fn = match(p.name, p)
        if not fn:
            continue
        try:
            entries.extend(fn(root, p))
        except Exception as e:  # keep scanning; report the file instead of crashing
            errors.append({"path": rel(p, root), "error": f"{type(e).__name__}: {e}"})
    # Gradle: gradle.properties may be reported once per build/settings script.
    seen, unique = set(), []
    for e in entries:
        key = (e["path"], e["field"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    entries = unique

    names = {p.name for p in files}
    if not entries and any(n.endswith((".sh", ".bash")) for n in names):
        entries.append({"path": None, "ecosystem": "shell", "tool": "shell",
                        "reference": "references/ecosystems/shell.md", "field": "git tag",
                        "version": None, "status": "tag-versioned", "note": None})
    if any(n.endswith(".ps1") for n in names) and not any(n.endswith(".psd1") for n in names):
        entries.append({"path": None, "ecosystem": "powershell", "tool": "scripts",
                        "reference": "references/ecosystems/powershell.md", "field": "git tag",
                        "version": None, "status": "tag-versioned", "note": None})

    ok_versions = sorted({e["version"] for e in entries if e["status"] == "ok"})
    try:
        tag = subprocess.run(["git", "describe", "--tags", "--abbrev=0"], cwd=root,
                             capture_output=True, text=True).stdout.strip() or None
    except FileNotFoundError:
        tag = None
    return {
        "root": str(root),
        "files": entries,
        "references": sorted({e["reference"] for e in entries}),
        "distinct_versions": ok_versions,
        # Compare MAJOR.MINOR.PATCH only: preserved suffixes (-SNAPSHOT, +build,
        # -rockspecrevision) legitimately differ between files.
        "consensus": len({core(v) for v in ok_versions}) == 1,
        "latest_tag": tag,
        "errors": errors,
    }


# --- tools -----------------------------------------------------------------

def tool_candidates(root: Path, eco: str, tool: str, path: str | None) -> list[str]:
    d = (root / path).parent if path else root
    has = lambda n: (d / n).exists()  # noqa: E731
    if eco == "javascript":
        cmds = ["node"]
        if has("pnpm-lock.yaml"):
            cmds.append("pnpm")
        elif has("yarn.lock"):
            cmds.append("yarn")
        elif has("bun.lockb") or has("bun.lock"):
            cmds.append("bun")
        else:
            cmds.append("npm")
        if has("tsconfig.json"):
            cmds.append("tsc")
        return cmds
    if eco == "python":
        cmds = ["python3"]
        if has("uv.lock"):
            cmds.append("uv")
        return cmds
    if eco == "java-kotlin":
        if tool == "maven":
            return ["./mvnw"] if has("mvnw") else ["mvn"]
        return ["./gradlew"] if has("gradlew") else ["gradle"]
    if eco == "ruby":
        return ["gem", "bundle"] if has("Gemfile") else ["gem"]
    if eco == "dart":
        return ["flutter"] if "flutter:" in read(d / "pubspec.yaml") else ["dart"]
    table = {
        ("rust", "cargo"): ["cargo"], ("c-cpp", "cmake"): ["cmake"],
        ("c-cpp", "meson"): ["meson"], ("c-cpp", "autotools"): ["autoreconf"],
        ("php", "composer"): ["composer"], ("scala", "sbt"): ["sbt"],
        ("go", "go"): ["go"], ("dotnet", "msbuild"): ["dotnet"],
        ("dotnet", "nuget"): ["dotnet"], ("swift-objc", "swiftpm"): ["swift"],
        ("swift-objc", "cocoapods"): ["pod"], ("swift-objc", "xcode"): ["xcodebuild"],
        ("powershell", "module"): ["pwsh"],
    }
    return table.get((eco, tool), [])


def available(cmd: str, base: Path) -> str | None:
    if cmd.startswith("./"):
        p = base / cmd[2:]
        return str(p) if os.access(p, os.X_OK) else None
    if cmd == "tsc":
        local = base / "node_modules" / ".bin" / "tsc"
        if local.exists():
            return str(local)
    return shutil.which(cmd)


def tools(root: Path) -> dict:
    det = detect(root)
    result, seen = [], set()
    for e in det["files"]:
        base = (root / e["path"]).parent if e["path"] else root
        for cmd in tool_candidates(root, e["ecosystem"], e["tool"], e["path"]):
            key = (cmd, str(base))
            if key in seen:
                continue
            seen.add(key)
            where = available(cmd, base)
            result.append({"ecosystem": e["ecosystem"], "tool": e["tool"],
                           "directory": rel(base, root) or ".", "command": cmd,
                           "available": where is not None, "resolved": where})
    if any(e["ecosystem"] == "python" for e in det["files"]) and shutil.which("python3"):
        ok = subprocess.run(["python3", "-c", "import build"], capture_output=True).returncode == 0
        result.append({"ecosystem": "python", "tool": "build", "directory": ".",
                       "command": "python3 -m build", "available": ok, "resolved": None})
    missing = [r["command"] for r in result if not r["available"]]
    return {"commands": result, "missing": sorted(set(missing))}


# --- verify ----------------------------------------------------------------

def parse_check(p: Path) -> str | None:
    """Return an error string if the file fails to parse, else None."""
    name = p.name
    try:
        if name.endswith(".json"):
            json.loads(read(p))
        elif name.endswith(".toml"):
            if tomllib is None:
                return None
            tomllib.loads(read(p))
        elif name.endswith((".xml", ".csproj", ".fsproj", ".vbproj", ".props", ".nuspec")):
            ET.parse(p)
        elif name.endswith(".plist"):
            with open(p, "rb") as f:
                plistlib.load(f)
    except Exception as e:
        return f"{type(e).__name__}: {e}"
    return None


def core(v: str | None) -> str | None:
    m = CORE_RE.search(v or "")
    return m.group(0) if m else None


def verify(root: Path, expect: str) -> dict:
    det = detect(root)
    want = core(expect)
    checks, failed = [], False
    for e in det["files"]:
        if e["status"] == "tag-versioned":
            continue
        p = root / e["path"]
        err = parse_check(p)
        problem = None
        if err:
            problem = f"parse error: {err}"
        elif e["status"] != "ok":
            problem = f"{e['status']}: {e['note'] or 'check manually'}"
        elif core(e["version"]) != want:
            problem = f"version is {e['version']}, expected {expect}"
        manual = e["status"] == "unresolved" and not err
        checks.append({"path": e["path"], "field": e["field"], "version": e["version"],
                       "ok": problem is None, "manual": manual, "problem": problem})
        if problem and not manual:
            failed = True
    for err in det["errors"]:  # files whose extractor crashed, e.g. broken JSON
        checks.append({"path": err["path"], "field": None, "version": None,
                       "ok": False, "manual": False, "problem": f"parse error: {err['error']}"})
        failed = True
    return {"expect": expect, "checks": checks, "passed": not failed}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="repository root (default: .)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("detect")
    sub.add_parser("tools")
    v = sub.add_parser("verify")
    v.add_argument("--expect", required=True, help="the new version, e.g. 1.2.4")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}))
        return 2
    if args.cmd == "detect":
        out = detect(root)
    elif args.cmd == "tools":
        out = tools(root)
    else:
        out = verify(root, args.expect)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 1 if args.cmd == "verify" and not out["passed"] else 0


if __name__ == "__main__":
    sys.exit(main())

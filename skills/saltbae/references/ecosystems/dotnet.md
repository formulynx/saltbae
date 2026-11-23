# C# / F# / VB.NET

## MSBuild / NuGet

### Detection

- Any `*.csproj` / `*.fsproj` / `*.vbproj` at any depth, excluding `bin/` / `obj/`.
- `Directory.Build.props` at the solution/repo root. When it defines `<Version>` / `<VersionPrefix>`, treat it as the single canonical file to bump instead of editing the same property in every project file. MSBuild walks upward from each project directory and applies the first `Directory.Build.props` it finds to all projects under it.

### Version-bearing file

In priority order:

1. `<Version>`. A single MSBuild property holding the full semver string, including any prerelease suffix (e.g. `1.2.3-beta.1`). Canonical when present.
2. `<VersionPrefix>` / `<VersionSuffix>`. The split form: `VersionPrefix` is the base numeric semver and `VersionSuffix` is the prerelease label. MSBuild composes them into `$(Version)` only when `$(Version)` itself is not set. Bump `VersionPrefix` when this form is used.
3. `<AssemblyVersion>` / `<FileVersion>`, or in older non-SDK-style projects `[assembly: AssemblyVersion("...")]` / `[assembly: AssemblyFileVersion("...")]` in `AssemblyInfo.cs`. These are 4-part Windows-style versions (`Major.Minor.Build.Revision`), not semver. Leave them out of scope unless the repo already keeps them numerically in sync with `<Version>`.
4. A standalone `.nuspec`'s `<version>` element. Only legacy non-SDK-style projects hand-author one; SDK-style projects generate it at pack time from `<Version>`. Add it to the sync set if present.

### Bump-rule nuance

Apply the standard numeric patch-increment rule to whichever of tiers 1/2 is canonical. Never touch tier 3's 4-part fields in a routine bump unless they are already tracked in lockstep.

### Build/check

`dotnet build`, or `dotnet build -c Release`.

### Lockfile

None. `packages.lock.json` records dependencies, not the project's own version.

### Extra update steps

None.

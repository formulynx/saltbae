# C# / F# / VB.NET

## MSBuild / NuGet

### Version-bearing file

If `Directory.Build.props` defines the version, bump it there only, not in every project file. Otherwise, in priority order:

1. `<Version>`.
2. `<VersionPrefix>` (with an optional `<VersionSuffix>`) when `<Version>` is not set.
3. A hand-authored `.nuspec`'s `<version>` (legacy projects) → add to the sync set.

Leave `<AssemblyVersion>` / `<FileVersion>` / `AssemblyInfo.cs` attributes alone unless the repo already keeps them in lockstep.

### Build/check

`dotnet build`.

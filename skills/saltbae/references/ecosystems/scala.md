# Scala

## sbt

### Detection

`build.sbt` at the project root. `project/build.properties` corroborates it but pins the sbt launcher version (`sbt.version`), not the project's version. It is not a bump target.

### Version-bearing file

Use the first source that applies:

1. A dedicated `version.sbt` file. This is the `sbt-release` plugin's convention: a single `version := "x.y.z"` or `ThisBuild / version := "x.y.z"` line.
2. Else the `version :=` / `ThisBuild / version :=` line inside `build.sbt`.

### Bump-rule nuance

`-SNAPSHOT` denotes an in-development version. sbt routes snapshot and release artifacts to different repositories based on this suffix. It is exempt from the ask-the-user suffix rule in `SKILL.md`.

- Routine bump → auto-increment the numeric part and preserve `-SNAPSHOT` (`1.2.3-SNAPSHOT` → `1.2.4-SNAPSHOT`).
- Explicit release cut → strip it.
- Never treat `SNAPSHOT` as numeric content.

### Build/check

`sbt compile`.

### Lockfile

None.

### Extra update steps

None.

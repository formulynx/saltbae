# Scala

## sbt

### Version-bearing file

1. `version.sbt`, if present.
2. Otherwise the `version :=` / `ThisBuild / version :=` line in `build.sbt`.

`project/build.properties` holds the sbt launcher version, not the project's.

### Bump-rule nuance

Preserve `-SNAPSHOT` on a routine bump; strip it only on an explicit release cut.

### Build/check

`sbt compile`.

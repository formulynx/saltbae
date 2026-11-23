# Java / Kotlin

## Maven

### Detection

`pom.xml` at the project root or nearest ancestor. `mvnw` / `mvnw.cmd` wrapper scripts corroborate it.

### Version-bearing file

`pom.xml`'s `<version>` element that is a direct child of the root `<project>` element only.

- Never `/project/parent/version`. That is the parent POM's own version, used for inheritance.
- Never a `<dependencies>` / `<dependencyManagement>` `<version>`. That is a dependency constraint.
- A naive grep for `<version>` false-positives on both. Parse for the first `<version>` that is a direct sibling of `<groupId>` / `<artifactId>` under the top-level `<project>` node.
- Multi-module reactor child POMs often omit their own `<version>` and inherit from `<parent>`. The version then lives only in the root/parent POM.
- CI-friendly versions (Maven 3.5+): the root POM's `<version>` may be the placeholder `${revision}` (optionally with `${sha1}` / `${changelist}`). The real value is in `<properties><revision>x.y.z</revision></properties>` in the same POM, or in `.mvn/maven.config`. The bump target is then the `<revision>` property's value, not the literal `<version>` text.

### Bump-rule nuance

`-SNAPSHOT` denotes an in-development, unreleased version. It is a perpetual flag, not a prerelease choice, so it is exempt from the ask-the-user suffix rule in `SKILL.md`.

- Routine bump → auto-increment the numeric part and preserve `-SNAPSHOT` (`1.2.3-SNAPSHOT` → `1.2.4-SNAPSHOT`).
- Explicit release cut → strip it (`1.2.3-SNAPSHOT` → `1.2.3`).
- Never treat `SNAPSHOT` as a token to increment.

### Build/check

`mvn -q -DskipTests compile`, or the lighter `mvn validate`.

### Lockfile

None.

### Extra update steps

None.

## Gradle

### Detection

Any of `build.gradle`, `build.gradle.kts`, `settings.gradle`, `settings.gradle.kts` at the project root. `gradlew` / `gradlew.bat` wrapper scripts corroborate it. Kotlin projects disproportionately use the `.kts` variants.

### Version-bearing file

Use the first source that applies:

1. `gradle.properties`'s top-level `version=x.y.z` line. This file loads before any build script executes.
2. Else the inline `version = "x.y.z"` assignment in `build.gradle` / `build.gradle.kts`.

`Project.version` defaults to the literal string `"unspecified"` if neither is set.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

`./gradlew build -x test`, or `./gradlew check`.

### Lockfile

None.

### Extra update steps

None.

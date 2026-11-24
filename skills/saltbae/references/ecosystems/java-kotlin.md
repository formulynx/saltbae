# Java / Kotlin

## Maven

### Version-bearing file

- The `<version>` that is a direct child of the root `<project>`. Never `<parent><version>` or a dependency `<version>`.
- Child POMs without their own `<version>` inherit it; leave them.
- `<version>${revision}</version>` → edit `<properties><revision>` in the same POM, or `.mvn/maven.config`.

### Bump-rule nuance

Preserve `-SNAPSHOT` on a routine bump (`1.2.3-SNAPSHOT` → `1.2.4-SNAPSHOT`). Strip it only on an explicit release cut.

### Build/check

`mvn -q -DskipTests compile` (`./mvnw` when present).

## Gradle

### Detection

`build.gradle(.kts)` or `settings.gradle(.kts)`.

### Version-bearing file

1. `version=` in `gradle.properties`.
2. Otherwise `version = "x.y.z"` in `build.gradle(.kts)`.

Neither set → tag-versioned.

### Build/check

`./gradlew build -x test`.

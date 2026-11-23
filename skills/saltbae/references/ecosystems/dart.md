# Dart / Flutter

## pub

### Detection

`pubspec.yaml` at the repo root, or at a package root in a monorepo/melos workspace. It is the sole manifest format for both plain Dart and Flutter packages.

### Version-bearing file

`pubspec.yaml`'s top-level `version:` key, format `major.minor.patch[+buildNumber]` (e.g. `1.2.3+45`).

- `major.minor.patch` maps to Android's `versionName` / iOS's `CFBundleShortVersionString` (`--build-name`).
- `+buildNumber` maps to Android's `versionCode` / iOS's `CFBundleVersion` (`--build-number`).

### Bump-rule nuance

`+buildNumber` is exempt from the ask-the-user suffix rule in `SKILL.md`.

- Bump only the `major.minor.patch` part with the standard numeric patch-increment rule.
- Leave `+buildNumber` unchanged. dart.dev defines no bump policy for it, and it is commonly CI-managed out-of-band.
- If the current version has no `+N`, do not introduce one.

### Build/check

- Flutter app → `flutter build`.
- Pure-Dart package → `dart pub get && dart analyze`.

### Lockfile

None. `pubspec.lock` records dependencies, not the package's own version.

### Extra update steps

None.

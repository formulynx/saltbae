# Dart / Flutter

## pub

### Version-bearing file

`version:` in `pubspec.yaml`, format `major.minor.patch[+buildNumber]`.

### Bump-rule nuance

Bump `major.minor.patch` only. Preserve `+buildNumber` unchanged, and do not add one if absent.

### Build/check

Flutter app → `flutter build`. Pure Dart → `dart pub get && dart analyze`.

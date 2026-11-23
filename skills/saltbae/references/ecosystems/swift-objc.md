# Swift / Objective-C

Objective-C shares Swift's Xcode and CocoaPods rules entirely. Build settings and `Info.plist` attach to a target, not a source language, and a `.podspec` describes a Pod regardless of whether `source_files` matches `.m` or `.swift`.

SwiftPM, CocoaPods and Xcode are independent and commonly coexist. Check all three and update whichever are present, in sync.

## SwiftPM

### Detection

`Package.swift`.

### Version-bearing file

None, by design. The `Package` initializer has no `version` parameter. A pure-SPM package is tag-versioned (`1.0.0` or `v1.0.0`), and the git tag is the primary source. Bumping means tagging, with no file diff.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

`swift build`.

### Lockfile

None. `Package.resolved` records dependencies, not the package's own version.

### Extra update steps

None.

## CocoaPods

### Detection

`*.podspec`.

### Version-bearing file

`spec.version = 'x.y.z'`. A required field, settable on the root specification only.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

`pod lib lint`.

### Lockfile

None.

### Extra update steps

None.

## Xcode

### Detection

`*.xcodeproj` / `*.xcworkspace`.

### Version-bearing file

Check which form is present:

(a) Modern (Xcode 11+): the `MARKETING_VERSION` build setting in `project.pbxproj`, one value per build configuration. Update all occurrences. `Info.plist`'s `CFBundleShortVersionString` holds the literal `$(MARKETING_VERSION)`.

(b) Legacy: `Info.plist`'s `CFBundleShortVersionString` holds the version as a hardcoded literal. Edit it in place if `MARKETING_VERSION` is absent from `project.pbxproj`.

(c) `Info.plist` contains `$(MARKETING_VERSION)` but no `MARKETING_VERSION` key exists in `project.pbxproj` → the project is inconsistent. Flag it for the user rather than guessing.

Never confuse either form with `CURRENT_PROJECT_VERSION` / `CFBundleVersion`. That pair is a build number, incremented per build/submission, independent of the marketing version. Do not bump it.

### Bump-rule nuance

None beyond the general rule in `SKILL.md`.

### Build/check

1. `xcodebuild -list -json [-project X.xcodeproj | -workspace X.xcworkspace]` to enumerate targets, schemes and configurations.
2. `xcodebuild build -scheme <resolved-scheme> -quiet`.

When several schemes exist, which one to build is not mechanically decidable from the JSON. Ask the user.

### Lockfile

None.

### Extra update steps

None.

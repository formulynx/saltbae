# Swift / Objective-C

SwiftPM, CocoaPods and Xcode commonly coexist; update every one present. Objective-C follows the same rules.

## SwiftPM

### Version-bearing file

None; `Package.swift` has no version field. Tag-versioned.

### Build/check

`swift build`.

## CocoaPods

### Version-bearing file

`spec.version` in the `.podspec`.

### Build/check

`pod lib lint`.

## Xcode

### Version-bearing file

(a) `MARKETING_VERSION` in `project.pbxproj` → update every occurrence.

(b) No `MARKETING_VERSION` → the literal `CFBundleShortVersionString` in `Info.plist`.

(c) `Info.plist` references `$(MARKETING_VERSION)` but `project.pbxproj` lacks it → ask the user.

Never bump `CURRENT_PROJECT_VERSION` / `CFBundleVersion`; that is the build number.

### Build/check

Find the scheme with `xcodebuild -list -json`, then `xcodebuild build -scheme <scheme> -quiet`. If several schemes exist, ask the user which to build.

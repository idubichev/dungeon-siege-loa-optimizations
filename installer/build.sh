#!/bin/bash
# Builds "Dungeon Siege Installer.app" and a zip for GitHub Releases.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=..
OUT=build
APP="$OUT/Dungeon Siege Installer.app"
rm -rf "$OUT" && mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"

# Some Command Line Tools releases ship a duplicate Swift module map; hide it if present.
FLAGS=()
CLT=/Library/Developer/CommandLineTools/usr/include/swift
if [ -f "$CLT/module.modulemap" ] && [ -f "$CLT/bridging.modulemap" ]; then
  : > "$OUT/empty.modulemap"
  printf '{"version":0,"roots":[{"name":"%s/bridging.modulemap","type":"file","external-contents":"%s/empty.modulemap"}]}' "$CLT" "$PWD/$OUT" > "$OUT/overlay.yaml"
  FLAGS=(-vfsoverlay "$OUT/overlay.yaml" -Xcc -ivfsoverlay -Xcc "$OUT/overlay.yaml")
fi
for arch in arm64 x86_64; do
  swiftc -O "${FLAGS[@]}" -target "$arch-apple-macos13.0" -o "$OUT/installer-$arch" main.swift
done
lipo -create -output "$APP/Contents/MacOS/Dungeon Siege Installer" "$OUT/installer-arm64" "$OUT/installer-x86_64"

cp "$ROOT/patches/manifest.json" "$ROOT/patches/DSLOA.exe.bps" "$ROOT/patches/D3DImm.dll.bps" "$ROOT/config/dxvk.conf" "$APP/Contents/Resources/"
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleExecutable</key><string>Dungeon Siege Installer</string>
  <key>CFBundleIdentifier</key><string>io.github.idubichev.dungeonsiege-installer</string>
  <key>CFBundleName</key><string>Dungeon Siege Installer</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>LSMinimumSystemVersion</key><string>13.0</string>
  <key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
codesign --force --deep -s - "$APP"
(cd "$OUT" && ditto -c -k --norsrc --noextattr --keepParent "Dungeon Siege Installer.app" "Dungeon-Siege-Installer.zip")
rm -f "$OUT"/installer-* "$OUT"/empty.modulemap "$OUT"/overlay.yaml
echo "Built $OUT/Dungeon-Siege-Installer.zip"

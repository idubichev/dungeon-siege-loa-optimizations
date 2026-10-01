#!/bin/zsh
set -euo pipefail
profile_contents='$HOME/Applications/Dungeon Siege Profile Test.app/Contents'
export WINEPREFIX="$profile_contents/SharedSupport/prefix"
export DYLD_FALLBACK_LIBRARY_PATH="$profile_contents/Frameworks"
export WINEESYNC="$1"
export WINEMSYNC="$2"
export WINEDEBUG="${4:--all}"
export MVK_CONFIG_FULL_IMAGE_VIEW_SWIZZLE=1
cd "$WINEPREFIX/drive_c/GOG Games/Dungeon Siege"
exec "$profile_contents/SharedSupport/${3:-wine}/bin/wine64" DSLOA.exe nointro=true fullscreen=false nospacecheck=true bltonly=true

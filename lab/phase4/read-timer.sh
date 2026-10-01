#!/bin/zsh
set -euo pipefail
contents='$HOME/Applications/Dungeon Siege Profile Test.app/Contents'
export WINEPREFIX="$contents/SharedSupport/prefix"
export DYLD_FALLBACK_LIBRARY_PATH="$contents/Frameworks"
export WINEESYNC=1 WINEMSYNC=1 WINEDEBUG=-all MVK_CONFIG_LOG_LEVEL=0
exec "$contents/SharedSupport/wine/bin/wine64" 'Z:\Users\you\Library\Application Support\Dungeon Siege Optimized\python-win32\pythonw.exe' 'Z:\Users\you\Documents\Dungeon Siege 1\experiments\2026-09-06\phase4\read-function-timer.py' "$1" "${2:-8}" "${3:-02-render-timer}"

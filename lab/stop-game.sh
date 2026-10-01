#!/bin/zsh
set -eu
root='$HOME/Applications/Dungeon Siege Wine10 Test.app/Contents'
env WINEPREFIX="$root/SharedSupport/prefix" DYLD_FALLBACK_LIBRARY_PATH="$root/Frameworks" "$root/SharedSupport/wine/bin/wineserver" -k
for i in 1 2 3 4 5; do
 if ! ps -axo comm= | /usr/bin/grep -q 'DSLOA.exe'; then exit 0; fi
 sleep 1
done
exit 1

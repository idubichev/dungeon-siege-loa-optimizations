#!/bin/bash
# Double-click to install the Dungeon Siege performance patch.
cd "$(dirname "$0")" || exit 1
clear
echo "Dungeon Siege performance patch"
echo "Quit Dungeon Siege before continuing."
echo
/usr/bin/python3 patch.py --install-renderer --install-dxvk
echo
read -n 1 -s -r -p "Press any key to close this window."

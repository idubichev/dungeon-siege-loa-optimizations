#!/bin/bash
# Double-click to put the original Dungeon Siege files back.
cd "$(dirname "$0")" || exit 1
clear
echo "Dungeon Siege performance patch: uninstall"
echo
/usr/bin/python3 patch.py --restore
echo
read -n 1 -s -r -p "Press any key to close this window."

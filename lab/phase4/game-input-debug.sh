#!/bin/zsh
set -eux
exec > $HOME/Documents/ds-input-debug.log 2>&1
lab='$HOME/Documents/Dungeon Siege 1/experiments/2026-09-06'
read game_pid game_window < <("$lab/windows" | /opt/homebrew/bin/python3 -c 'import sys,json; a=[json.loads(s) for s in sys.stdin]; a=[w for w in a if w.get("kCGWindowName")=="Dungeon Siege"]; assert len(a)==1; print(a[0]["kCGWindowOwnerPID"],a[0]["kCGWindowNumber"])')
/usr/bin/osascript -e "tell application \"System Events\" to set frontmost of first application process whose unix id is $game_pid to true"
sleep 0.3
/opt/homebrew/bin/cliclick "$@"
sleep 0.8

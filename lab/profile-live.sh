#!/bin/zsh

set -euo pipefail

workspace='$HOME/Documents/Dungeon Siege 1'
test_app='$HOME/Applications/Dungeon Siege Wine10 Test.app'

die() {
  print -u2 -- "profile-live: $*"
  exit 1
}

find_game_pid() {
  local pid output
  local -a matches
  matches=()
  output="$(ps -axo pid=,comm=,args= | \
    awk '$0 ~ /DSLOA\.exe/ && $0 !~ /start\.exe/ { print $1 }')"

  for pid in ${(f)output}; do
    if lsof -n -P -p "$pid" 2>/dev/null | \
        grep -F "$test_app/Contents/SharedSupport" >/dev/null; then
      matches+=("$pid")
    fi
  done

  (( ${#matches[@]} == 1 )) || \
    die "expected one live DSLOA process from the isolated wrapper, found ${#matches[@]}"
  print -- "$matches[1]"
}

show_status() {
  local pid
  print -- 'Visible Dungeon Siege processes:'
  ps -axo pid=,ppid=,state=,%cpu=,etime=,comm=,args= | \
    awk '$0 ~ /DSLOA\.exe/ && $0 !~ /awk .*DSLOA/ { print }'

  if pid="$(find_game_pid 2>/dev/null)"; then
    print -- "Verified isolated-wrapper game PID: $pid"
  else
    print -- 'Verified isolated-wrapper game PID: none'
  fi
}

capture_sample() {
  local pid stamp output
  pid="$(find_game_pid)"
  stamp="$(date '+%Y%m%d-%H%M%S')"
  mkdir -p "$workspace/profiles"
  output="$workspace/profiles/DSLOA-$stamp.sample.txt"

  print -- "Sampling isolated-wrapper DSLOA PID $pid for 8 seconds..."
  /usr/bin/sample "$pid" 8 1 -mayDie -fullPaths -file "$output"
  [[ -s "$output" ]] || die 'sample completed without a report'
  print -- "Sample report: $output"
}

case "${1:-}" in
  status)
    show_status
    ;;
  sample)
    capture_sample
    ;;
  *)
    print -- 'Usage: profile-live.sh <status|sample>'
    exit 2
    ;;
esac

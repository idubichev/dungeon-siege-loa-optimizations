#!/bin/zsh

set -euo pipefail

workspace='$HOME/Documents/Dungeon Siege 1'
test_app='$HOME/Applications/Dungeon Siege Wine10 Test.app'
target="$test_app/Contents/Frameworks/libMoltenVK.dylib"
candidate="$workspace/renderer-candidates/moltenvk-1.4.1/unpacked/libMoltenVK.dylib"
bundled_reference='$HOME/Applications/Dungeon Siege.app/Contents/Frameworks/libMoltenVK.dylib'
lab_dir="$workspace/moltenvk-lab-state"
bundled="$lab_dir/bundled/libMoltenVK.dylib"

die() {
  print -u2 -- "moltenvk-lab: $*"
  exit 1
}

require_idle_game() {
  if ps -axo comm=,args= | grep -E '(^|[[:space:]\\/])DSLOA\.exe([[:space:]]|$)' >/dev/null; then
    die 'DSLOA.exe is running; close the isolated test game before changing MoltenVK'
  fi
}

require_layout() {
  [[ -f "$target" ]] || die "isolated wrapper MoltenVK is missing: $target"
  [[ "$target" == *'Dungeon Siege Wine10 Test.app/'* ]] || \
    die 'refusing to operate outside the isolated test wrapper'
  [[ -f "$candidate" ]] || die "MoltenVK 1.4.1 candidate is missing: $candidate"
  [[ -f "$bundled_reference" ]] || \
    die "read-only bundled MoltenVK reference is missing: $bundled_reference"
}

snapshot_bundled() {
  [[ -f "$bundled" ]] && return 0
  mkdir -p "${bundled:h}"
  cp -p "$bundled_reference" "$bundled"
  print -- 'Captured the isolated wrapper bundled MoltenVK.'
}

archive_current() {
  local stamp history
  stamp="$(date '+%Y%m%d-%H%M%S')"
  mkdir -p "$lab_dir/history"
  history="$(mktemp -d "$lab_dir/history/$stamp.XXXXXX")"
  cp -p "$target" "$history/libMoltenVK.dylib"
}

show_status() {
  local profile='unknown'
  if cmp -s "$target" "$bundled_reference"; then
    profile='bundled'
  elif cmp -s "$target" "$candidate"; then
    profile='mvk141'
  fi
  print -- "MoltenVK profile: $profile"
  file "$target"
  LC_ALL=C openssl dgst -sha256 "$target"
}

usage() {
  print -- 'Usage: moltenvk-lab.sh <status|bundled|mvk141>'
}

require_layout

case "${1:-}" in
  status)
    show_status
    ;;
  bundled|mvk141)
    require_idle_game
    snapshot_bundled
    archive_current
    case "$1" in
      bundled)
        cp -p "$bundled" "$target"
        ;;
      mvk141)
        cp -p "$candidate" "$target"
        ;;
    esac
    print -- "Applied MoltenVK profile: $1"
    show_status
    ;;
  *)
    usage
    exit 2
    ;;
esac

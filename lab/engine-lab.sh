#!/bin/zsh

set -euo pipefail

source_app='$HOME/Applications/Dungeon Siege Wine10 Test.app'
target_app='$HOME/Applications/Dungeon Siege CX23 Test.app'
source_support="$source_app/Contents/SharedSupport"
source_game="$source_support/prefix/drive_c/GOG Games/Dungeon Siege"
source_plist="$source_app/Contents/Info.plist"
expected_ddraw='6035b806cd001f6c1ac967d1d0574ed52ed6d354b36b1426c052ac4167ae9c16'
expected_d3d11='f79d417f675d00008375eb4ea2318af6fcd0b27971d604d3cf345a0dcfa998a0'
expected_mvk='c85a99c7059b44bf00ccecd61ffe185197452beef126aa39f5086fafeb099559'

die() {
  print -u2 -- "engine-lab: $*"
  exit 1
}

sha256() {
  /usr/bin/openssl dgst -sha256 "$1" | awk '{ print $2 }'
}

require_layout() {
  [[ -d "$source_support/wine" && -d "$source_support/wine-cx23-original" ]] || \
    die 'source wrapper does not contain both engine directories'
  [[ -f "$source_support/wine/version" && -f "$source_support/wine-cx23-original/version" ]] || \
    die 'source engine version metadata is incomplete'
  [[ "$(<"$source_support/wine/version")" == *'sikarugir 10.0'* ]] || \
    die 'source active engine is not the expected Wine 10 build'
  [[ "$(<"$source_support/wine-cx23-original/version")" == *'WineskinCX 23.7.1'* ]] || \
    die 'stored CrossOver engine is not the expected 23.7.1 build'
}

require_idle_source() {
  if ps -axo comm=,args= | grep -E '(^|[[:space:]\\/])DSLOA\.exe([[:space:]]|$)' >/dev/null; then
    die 'DSLOA launch or helper processes still exist; reboot or clear them before cloning'
  fi
  if ps -axo args= | grep -F "$source_app/Contents/SharedSupport" | grep -v -E 'grep -F|engine-lab\.sh' >/dev/null; then
    die 'the source wrapper still has Wine processes; reboot or clear them before cloning'
  fi
}

require_clean_source() {
  local flags
  [[ "$(sha256 "$source_game/DDraw.dll")" == "$expected_ddraw" ]] || \
    die 'source DDraw.dll is not the clean dgVoodoo 2.53 baseline'
  [[ "$(sha256 "$source_game/d3d11.dll")" == "$expected_d3d11" ]] || \
    die 'source d3d11.dll is not the clean Gcenx DXVK baseline'
  [[ "$(sha256 "$source_app/Contents/Frameworks/libMoltenVK.dylib")" == "$expected_mvk" ]] || \
    die 'source MoltenVK is not the bundled baseline'
  flags="$(/usr/libexec/PlistBuddy -c "Print :'Program Flags'" "$source_plist")"
  [[ "$flags" == 'nointro=true fullscreen=false nospacecheck=true bltonly=true' ]] || \
    die 'source runtime flags are not the clean production baseline; run fps-test.sh restore first'
}

show_status() {
  print -- "Source active engine: $(<"$source_support/wine/version")"
  print -- "Source stored engine: $(<"$source_support/wine-cx23-original/version")"
  if [[ -d "$target_app" ]]; then
    print -- "CX23 clone: present"
    print -- "CX23 active engine: $(<"$target_app/Contents/SharedSupport/wine/version")"
  else
    print -- 'CX23 clone: absent'
  fi
}

prepare_cx23_clone() {
  local temp_parent clone support plist
  require_idle_source
  require_clean_source
  [[ ! -e "$target_app" ]] || die "target already exists: $target_app"

  temp_parent="$(mktemp -d '$HOME/Applications/.ds-cx23-clone.XXXXXX')"
  clone="$temp_parent/Dungeon Siege CX23 Test.app"
  cp -cR "$source_app" "$clone"
  support="$clone/Contents/SharedSupport"
  plist="$clone/Contents/Info.plist"

  mv "$support/wine" "$support/wine-wine10-original"
  mv "$support/wine-cx23-original" "$support/wine"
  /usr/libexec/PlistBuddy -c 'Set :CFBundleName Dungeon Siege CX23 Test' "$plist"
  /usr/libexec/PlistBuddy -c 'Set :CFBundleIdentifier com.DungeonSiegeCX23Test824224639.wineskin' "$plist"
  plutil -lint "$plist" >/dev/null
  [[ "$(<"$support/wine/version")" == *'WineskinCX 23.7.1'* ]] || \
    die "clone verification failed; incomplete clone remains at $clone"
  [[ -d "$support/wine-wine10-original" ]] || \
    die "Wine 10 rollback engine is missing; incomplete clone remains at $clone"

  mv "$clone" "$target_app"
  rmdir "$temp_parent"
  print -- "Prepared isolated CrossOver engine clone: $target_app"
  show_status
}

require_layout

case "${1:-}" in
  status)
    show_status
    ;;
  prepare-cx23-clone)
    prepare_cx23_clone
    ;;
  *)
    print -- 'Usage: engine-lab.sh <status|prepare-cx23-clone>'
    exit 2
    ;;
esac

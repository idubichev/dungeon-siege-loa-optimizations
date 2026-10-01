#!/bin/zsh

set -euo pipefail

workspace='$HOME/Documents/Dungeon Siege 1'
prefs='$HOME/Documents/Dungeon Siege LOA/prefs.gas'
lab_dir="$workspace/prefs-lab-state"
initial_prefs="$lab_dir/initial/prefs.gas"

die() {
  print -u2 -- "prefs-lab: $*"
  exit 1
}

require_idle_game() {
  if ps -axo comm=,args= | grep -E '(^|[[:space:]\\/])DSLOA\.exe([[:space:]]|$)' >/dev/null; then
    die 'DSLOA.exe is running; close the test game before changing preferences'
  fi
}

require_layout() {
  [[ -f "$prefs" ]] || die "active LoA preferences are missing: $prefs"
  [[ "$prefs" == '$HOME/Documents/Dungeon Siege LOA/prefs.gas' ]] || \
    die 'refusing to operate outside the active LoA preferences file'
  rg -q '^\[prefs\]\r?$' "$prefs" || die 'the target does not look like a Dungeon Siege preferences file'
}

snapshot_initial() {
  [[ -f "$initial_prefs" ]] && return 0
  mkdir -p "${initial_prefs:h}"
  cp -p "$prefs" "$initial_prefs"
  print -- 'Captured the current LoA preferences.'
}

archive_current() {
  local stamp history
  stamp="$(date '+%Y%m%d-%H%M%S')"
  mkdir -p "$lab_dir/history"
  history="$(mktemp -d "$lab_dir/history/$stamp.XXXXXX")"
  cp -p "$prefs" "$history/prefs.gas"
}

replace_pref() {
  local key="$1"
  local value="$2"
  local count

  count="$(PREFS_LAB_KEY="$key" /usr/bin/perl -ne '
    BEGIN { $key = $ENV{"PREFS_LAB_KEY"}; $count = 0 }
    $count++ if /^[ \t]*\Q$key\E[ \t]*=/;
    END { print $count }
  ' "$prefs")"
  [[ "$count" == 1 ]] || die "expected exactly one $key entry, found $count"

  PREFS_LAB_KEY="$key" PREFS_LAB_VALUE="$value" /usr/bin/perl -0pi -e '
    BEGIN {
      $key = $ENV{"PREFS_LAB_KEY"};
      $value = $ENV{"PREFS_LAB_VALUE"};
    }
    s/^([ \t]*)\Q$key\E[ \t]*=[ \t]*[^;\r\n]+;/$1$key = $value;/m;
  ' "$prefs"
}

set_baseline() {
  replace_pref priority_boost false
  replace_pref object_detail_level 1.000000
  replace_pref show_framerate true
  replace_pref sound_enabled false
}

verify_prefs() {
  rg -q '^\[prefs\]\r?$' "$prefs" || die 'preferences verification failed'
  for key in priority_boost object_detail_level show_framerate sound_enabled; do
    [[ "$(rg -c "^[[:space:]]*$key[[:space:]]*=" "$prefs")" == 1 ]] || \
      die "preferences verification failed for $key"
  done
}

show_status() {
  print -- "Preferences: $prefs"
  rg -n '^[[:space:]]*(priority_boost|object_detail_level|show_framerate|sound_enabled|video_shadows|texture_filtering)[[:space:]]*=' "$prefs"
}

usage() {
  print -- 'Usage: prefs-lab.sh <status|restore-initial|baseline|priority-boost-on|detail-75|detail-50|detail-25|detail-20|priority-detail-50>'
}

require_layout

case "${1:-}" in
  status)
    show_status
    ;;
  restore-initial|baseline|priority-boost-on|detail-75|detail-50|detail-25|detail-20|priority-detail-50)
    require_idle_game
    snapshot_initial
    archive_current
    case "$1" in
      restore-initial)
        cp -p "$initial_prefs" "$prefs"
        ;;
      baseline)
        set_baseline
        ;;
      priority-boost-on)
        set_baseline
        replace_pref priority_boost true
        ;;
      detail-75)
        set_baseline
        replace_pref object_detail_level 0.750000
        ;;
      detail-50)
        set_baseline
        replace_pref object_detail_level 0.500000
        ;;
      detail-25)
        set_baseline
        replace_pref object_detail_level 0.250000
        ;;
      detail-20)
        set_baseline
        replace_pref object_detail_level 0.200000
        ;;
      priority-detail-50)
        set_baseline
        replace_pref priority_boost true
        replace_pref object_detail_level 0.500000
        ;;
    esac
    verify_prefs
    print -- "Applied preferences profile: $1"
    show_status
    ;;
  *)
    usage
    exit 2
    ;;
esac

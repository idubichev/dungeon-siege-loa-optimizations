#!/bin/zsh

set -euo pipefail

workspace='$HOME/Documents/Dungeon Siege 1'
test_app='$HOME/Applications/Dungeon Siege Wine10 Test.app'
game_dir="$test_app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege"
lab_dir="$workspace/resources-lab-state"
initial_dir="$lab_dir/initial"

managed_resources=(
  'Resources/fairyfix.dsres'
  'Resources/ikkyo_mpsave_beta_6.dsres'
  'Resources/sf_ResolutionFix.dsres'
  'DSLOA/DS1_Difficulty_Patch.dsres'
  'DSLOA/UberUI_LoA_v0.02.dsres'
)

die() {
  print -u2 -- "resources-lab: $*"
  exit 1
}

require_idle_game() {
  if ps -axo comm=,args= | grep -E '(^|[[:space:]\\/])DSLOA\.exe([[:space:]]|$)' >/dev/null; then
    die 'DSLOA.exe is running; close the isolated test game before changing resources'
  fi
}

require_layout() {
  [[ -d "$game_dir/Resources" && -d "$game_dir/DSLOA" ]] || \
    die 'isolated game resource directories are missing'
  [[ "$game_dir" == *'Dungeon Siege Wine10 Test.app/'* ]] || \
    die 'refusing to operate outside the isolated test wrapper'
}

snapshot_initial() {
  local relative
  if [[ -f "$initial_dir/complete" ]]; then
    for relative in "${managed_resources[@]}"; do
      [[ -f "$initial_dir/$relative" ]] || die "initial snapshot is missing $relative"
    done
    return 0
  fi

  for relative in "${managed_resources[@]}"; do
    [[ -f "$game_dir/$relative" ]] || \
      die "cannot capture initial resource set; missing $relative"
  done
  for relative in "${managed_resources[@]}"; do
    mkdir -p "$initial_dir/${relative:h}"
    cp -p "$game_dir/$relative" "$initial_dir/$relative"
  done
  : > "$initial_dir/complete"
  print -- 'Captured the initial optional-resource set.'
}

archive_current() {
  local stamp history relative
  stamp="$(date '+%Y%m%d-%H%M%S')"
  mkdir -p "$lab_dir/history"
  history="$(mktemp -d "$lab_dir/history/$stamp.XXXXXX")"
  for relative in "${managed_resources[@]}"; do
    if [[ -f "$game_dir/$relative" ]]; then
      mkdir -p "$history/${relative:h}"
      mv "$game_dir/$relative" "$history/$relative"
    fi
  done
}

enable_resource() {
  local relative="$1"
  cp -p "$initial_dir/$relative" "$game_dir/$relative"
}

apply_profile() {
  local profile="$1"
  local relative
  for relative in "${managed_resources[@]}"; do
    case "$profile:$relative" in
      minimal:*) ;;
      no-fairyfix:Resources/fairyfix.dsres) ;;
      no-mp-save:Resources/ikkyo_mpsave_beta_6.dsres) ;;
      no-resolution-fix:Resources/sf_ResolutionFix.dsres) ;;
      no-difficulty:DSLOA/DS1_Difficulty_Patch.dsres) ;;
      no-uberui:DSLOA/UberUI_LoA_v0.02.dsres) ;;
      *) enable_resource "$relative" ;;
    esac
  done
}

show_status() {
  local relative state
  for relative in "${managed_resources[@]}"; do
    if [[ -f "$game_dir/$relative" ]]; then
      state=enabled
    else
      state=disabled
    fi
    print -- "$state | $relative"
  done
}

usage() {
  print -- 'Usage: resources-lab.sh <status|restore|minimal|no-fairyfix|no-mp-save|no-resolution-fix|no-difficulty|no-uberui>'
}

require_layout

case "${1:-}" in
  status)
    show_status
    ;;
  restore|minimal|no-fairyfix|no-mp-save|no-resolution-fix|no-difficulty|no-uberui)
    require_idle_game
    snapshot_initial
    archive_current
    if [[ "$1" == restore ]]; then
      apply_profile all
    else
      apply_profile "$1"
    fi
    print -- "Applied optional-resource profile: $1"
    show_status
    ;;
  *)
    usage
    exit 2
    ;;
esac

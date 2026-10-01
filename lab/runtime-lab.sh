#!/bin/zsh

set -euo pipefail

workspace='$HOME/Documents/Dungeon Siege 1'
test_app='$HOME/Applications/Dungeon Siege Wine10 Test.app'
plist="$test_app/Contents/Info.plist"
lab_dir="$workspace/runtime-lab-state"
initial_plist="$lab_dir/initial/Info.plist"
recommended_flags='nointro=true fullscreen=false nospacecheck=true bltonly=true'
mvk_target="$test_app/Contents/Frameworks/libMoltenVK.dylib"
mvk_candidate="$workspace/renderer-candidates/moltenvk-1.4.1/unpacked/libMoltenVK.dylib"

die() {
  print -u2 -- "runtime-lab: $*"
  exit 1
}

require_idle_game() {
  if ps -axo comm=,args= | grep -E '(^|[[:space:]\\/])DSLOA\.exe([[:space:]]|$)' >/dev/null; then
    die 'DSLOA.exe is running; close the isolated test game before changing runtime settings'
  fi
}

require_layout() {
  [[ -f "$plist" ]] || die "isolated wrapper plist is missing: $plist"
  [[ "$plist" == *'Dungeon Siege Wine10 Test.app/'* ]] || die 'refusing to operate outside the isolated test wrapper'
}

snapshot_initial() {
  [[ -f "$initial_plist" ]] && return 0
  mkdir -p "${initial_plist:h}"
  cp -p "$plist" "$initial_plist"
  print -- 'Captured the current isolated-wrapper runtime settings.'
}

archive_current() {
  local stamp history
  stamp="$(date '+%Y%m%d-%H%M%S')"
  mkdir -p "$lab_dir/history"
  history="$(mktemp -d "$lab_dir/history/$stamp.XXXXXX")"
  cp -p "$plist" "$history/Info.plist"
}

set_flags() {
  /usr/libexec/PlistBuddy -c "Set :'Program Flags' $1" "$plist"
}

set_sync() {
  /usr/libexec/PlistBuddy -c "Set :WINEESYNC $1" "$plist"
  /usr/libexec/PlistBuddy -c "Set :WINEMSYNC $2" "$plist"
}

set_cli_commands() {
  /usr/libexec/PlistBuddy -c "Set :'CLI Custom Commands' $1" "$plist"
}

set_clean_runtime() {
  set_flags "$recommended_flags"
  set_sync 1 1
  /usr/libexec/PlistBuddy -c 'Set :WINEDEBUG -all' "$plist"
  /usr/libexec/PlistBuddy -c 'Set :METAL_HUD 0' "$plist"
  /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 1' "$plist"
  set_cli_commands ''
}

preflight_profile() {
  case "$1" in
    mvk141-default|mvk141-sync-submit|mvk141-async-submit|mvk141-async-single-queue|mvk141-perf-60|mvk141-trace-calls)
      [[ -f "$mvk_target" && -f "$mvk_candidate" ]] || \
        die 'MoltenVK 1.4.1 files are incomplete'
      cmp -s "$mvk_target" "$mvk_candidate" || \
        die 'this runtime profile requires moltenvk-lab.sh mvk141 first'
      ;;
  esac
}

verify_plist() {
  plutil -lint "$plist" >/dev/null
}

show_status() {
  print -- "Program Flags: $(/usr/libexec/PlistBuddy -c "Print :'Program Flags'" "$plist")"
  print -- "WINEESYNC: $(/usr/libexec/PlistBuddy -c 'Print :WINEESYNC' "$plist")"
  print -- "WINEMSYNC: $(/usr/libexec/PlistBuddy -c 'Print :WINEMSYNC' "$plist")"
  print -- "WINEDEBUG: $(/usr/libexec/PlistBuddy -c 'Print :WINEDEBUG' "$plist")"
  print -- "METAL_HUD: $(/usr/libexec/PlistBuddy -c 'Print :METAL_HUD' "$plist")"
  print -- "MOLTENVKCX: $(/usr/libexec/PlistBuddy -c 'Print :MOLTENVKCX' "$plist")"
  print -- "CLI Custom Commands: $(/usr/libexec/PlistBuddy -c "Print :'CLI Custom Commands'" "$plist")"
}

usage() {
  print -- 'Usage: runtime-lab.sh <status|restore-initial|recommended|benchmark-dxvk|benchmark-metal|production|simple|async-cursor-off|no-sound|buffers-off|noflip-off|one-buffer|shadow-target-off|trilinear-off|present-min|render-min|diagnostic-bpp16|diagnostic-notextures|sync-both|sync-esync|sync-msync|sync-none|quiet-logging|metal-hud-on|metal-hud-off|mvk-cx|mvk-stock|mvk-stock-no-args|mvk-argbuffers-off|mvk-sync-submit|mvk-async-submit|mvk-single-queue|mvk-async-single-queue|mvk141-default|mvk141-sync-submit|mvk141-async-submit|mvk141-async-single-queue|mvk141-perf-60|mvk141-trace-calls|mvk-default|dxmt-default|dxmt-quiet|dxmt-paced-60>'
}

require_layout

case "${1:-}" in
  status)
    show_status
    ;;
  restore-initial|recommended|benchmark-dxvk|benchmark-metal|production|simple|async-cursor-off|no-sound|buffers-off|noflip-off|one-buffer|shadow-target-off|trilinear-off|present-min|render-min|diagnostic-bpp16|diagnostic-notextures|sync-both|sync-esync|sync-msync|sync-none|quiet-logging|metal-hud-on|metal-hud-off|mvk-cx|mvk-stock|mvk-stock-no-args|mvk-argbuffers-off|mvk-sync-submit|mvk-async-submit|mvk-single-queue|mvk-async-single-queue|mvk141-default|mvk141-sync-submit|mvk141-async-submit|mvk141-async-single-queue|mvk141-perf-60|mvk141-trace-calls|mvk-default|dxmt-default|dxmt-quiet|dxmt-paced-60)
    require_idle_game
    preflight_profile "$1"
    snapshot_initial
    archive_current
    case "$1" in
      restore-initial)
        cp -p "$initial_plist" "$plist"
        ;;
      recommended)
        set_flags "$recommended_flags"
        ;;
      benchmark-dxvk)
        set_clean_runtime
        ;;
      benchmark-metal)
        set_clean_runtime
        /usr/libexec/PlistBuddy -c 'Set :METAL_HUD 1' "$plist"
        ;;
      production)
        set_clean_runtime
        ;;
      simple)
        set_flags "$recommended_flags simplerender=true"
        ;;
      async-cursor-off)
        set_flags "$recommended_flags asynccursor=false"
        ;;
      no-sound)
        set_flags "$recommended_flags nosound=true"
        ;;
      buffers-off)
        set_flags "$recommended_flags buffers_frames=false"
        ;;
      noflip-off)
        set_flags "$recommended_flags no_flip=false"
        ;;
      one-buffer)
        set_flags "$recommended_flags max_back_buffers=1"
        ;;
      shadow-target-off)
        set_flags "$recommended_flags shadow_render_target=false"
        ;;
      trilinear-off)
        set_flags "$recommended_flags trilinear_filt=false"
        ;;
      present-min)
        set_flags "$recommended_flags buffers_frames=false no_flip=false max_back_buffers=1"
        ;;
      render-min)
        set_flags "$recommended_flags simplerender=true buffers_frames=false no_flip=false max_back_buffers=1 shadow_render_target=false trilinear_filt=false"
        ;;
      diagnostic-bpp16)
        set_flags "$recommended_flags bpp=16"
        ;;
      diagnostic-notextures)
        set_flags "$recommended_flags notextures=true"
        ;;
      sync-both)
        set_sync 1 1
        ;;
      sync-esync)
        set_sync 1 0
        ;;
      sync-msync)
        set_sync 0 1
        ;;
      sync-none)
        set_sync 0 0
        ;;
      quiet-logging)
        /usr/libexec/PlistBuddy -c 'Set :WINEDEBUG -all' "$plist"
        ;;
      metal-hud-on)
        /usr/libexec/PlistBuddy -c 'Set :METAL_HUD 1' "$plist"
        ;;
      metal-hud-off)
        /usr/libexec/PlistBuddy -c 'Set :METAL_HUD 0' "$plist"
        ;;
      mvk-cx)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 1' "$plist"
        set_cli_commands ''
        ;;
      mvk-stock)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands ''
        ;;
      mvk-stock-no-args)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands 'export MVK_CONFIG_USE_METAL_ARGUMENT_BUFFERS=0;'
        ;;
      mvk-argbuffers-off)
        set_cli_commands 'export MVK_CONFIG_USE_METAL_ARGUMENT_BUFFERS=0;'
        ;;
      mvk-sync-submit)
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=0; export MVK_CONFIG_SYNCHRONOUS_QUEUE_SUBMITS=1;'
        ;;
      mvk-async-submit)
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=0; export MVK_CONFIG_SYNCHRONOUS_QUEUE_SUBMITS=0;'
        ;;
      mvk-single-queue)
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=0; export MVK_CONFIG_VK_SEMAPHORE_SUPPORT_STYLE=0;'
        ;;
      mvk-async-single-queue)
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=0; export MVK_CONFIG_SYNCHRONOUS_QUEUE_SUBMITS=0; export MVK_CONFIG_VK_SEMAPHORE_SUPPORT_STYLE=0;'
        ;;
      mvk141-default)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands ''
        ;;
      mvk141-sync-submit)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=0; export MVK_CONFIG_SYNCHRONOUS_QUEUE_SUBMITS=1;'
        ;;
      mvk141-async-submit)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=0; export MVK_CONFIG_SYNCHRONOUS_QUEUE_SUBMITS=0;'
        ;;
      mvk141-async-single-queue)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=0; export MVK_CONFIG_SYNCHRONOUS_QUEUE_SUBMITS=0; export MVK_CONFIG_VK_SEMAPHORE_SUPPORT_STYLE=0;'
        ;;
      mvk141-perf-60)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=3; export MVK_CONFIG_PERFORMANCE_TRACKING=1; export MVK_CONFIG_PERFORMANCE_LOGGING_FRAME_COUNT=60; export MVK_CONFIG_ACTIVITY_PERFORMANCE_LOGGING_STYLE=0;'
        ;;
      mvk141-trace-calls)
        /usr/libexec/PlistBuddy -c 'Set :MOLTENVKCX 0' "$plist"
        set_cli_commands 'export MVK_CONFIG_LOG_LEVEL=4; export MVK_CONFIG_TRACE_VULKAN_CALLS=6;'
        ;;
      mvk-default)
        set_cli_commands ''
        ;;
      dxmt-default)
        set_cli_commands ''
        ;;
      dxmt-quiet)
        set_cli_commands 'export DXMT_LOG_LEVEL=none;'
        ;;
      dxmt-paced-60)
        set_cli_commands 'export DXMT_LOG_LEVEL=none; export DXMT_CONFIG=d3d11.preferredMaxFrameRate=60;'
        ;;
    esac
    verify_plist
    print -- "Applied runtime profile: $1"
    show_status
    ;;
  *)
    usage
    exit 2
    ;;
esac

#!/bin/zsh

set -euo pipefail

workspace='$HOME/Documents/Dungeon Siege 1'
test_app='$HOME/Applications/Dungeon Siege Wine10 Test.app'
game_dir="$test_app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege"
lab_dir="$workspace/renderer-lab-state"
candidates="$workspace/renderer-candidates"
stable_dir="$lab_dir/stable"
reg_file="$test_app/Contents/SharedSupport/prefix/user.reg"
wine_root="$test_app/Contents/SharedSupport/wine"
prefix_root="$test_app/Contents/SharedSupport/prefix/drive_c/windows"
dxmt_source="$candidates/dxmt-v0.80/unpacked/v0.80"
dxmt_stable_dir="$lab_dir/dxmt-engine-stable"

managed_files=(
  DDraw.dll
  D3DImm.dll
  D3D8.dll
  d3d9.dll
  d3d10core.dll
  d3d11.dll
  dgVoodoo.conf
  dxvk.conf
  dxwrapper.dll
  dxwrapper.ini
  dxgl.ini
)

die() {
  print -u2 -- "renderer-lab: $*"
  exit 1
}

require_idle_game() {
  if ps -axo comm=,args= | grep -E '(^|[[:space:]\\/])DSLOA\.exe([[:space:]]|$)' >/dev/null; then
    die 'DSLOA.exe is running; close the isolated test game before changing renderers'
  fi
}

require_layout() {
  [[ -d "$game_dir" ]] || die "isolated game directory is missing: $game_dir"
  [[ -f "$game_dir/DSLOA.exe" ]] || die 'DSLOA.exe is missing from the isolated wrapper'
  [[ "$game_dir" == *'Dungeon Siege Wine10 Test.app/'* ]] || die 'refusing to operate outside the isolated test wrapper'
}

snapshot_stable() {
  local name
  if [[ -d "$stable_dir" ]]; then
    for name in DDraw.dll D3DImm.dll D3D8.dll d3d10core.dll d3d11.dll dgVoodoo.conf dxvk.conf; do
      [[ -f "$stable_dir/$name" ]] || die "stable snapshot is incomplete; missing $name"
    done
    return 0
  fi
  for name in DDraw.dll D3DImm.dll D3D8.dll d3d10core.dll d3d11.dll dgVoodoo.conf dxvk.conf; do
    [[ -f "$game_dir/$name" ]] || die "cannot create stable snapshot; missing $name"
  done
  mkdir -p "$stable_dir"
  for name in DDraw.dll D3DImm.dll D3D8.dll d3d10core.dll d3d11.dll dgVoodoo.conf dxvk.conf; do
    cp -p "$game_dir/$name" "$stable_dir/$name"
  done
  print -- 'Captured the current known-good renderer as the stable restore point.'
}

archive_current() {
  local stamp history name
  stamp="$(date '+%Y%m%d-%H%M%S')"
  mkdir -p "$lab_dir/history"
  history="$(mktemp -d "$lab_dir/history/$stamp.XXXXXX")"
  for name in "${managed_files[@]}"; do
    if [[ -e "$game_dir/$name" ]]; then
      mv "$game_dir/$name" "$history/$name"
    fi
  done
}

set_wined3d_renderer() {
  local renderer="$1"
  local count
  [[ -f "$reg_file" ]] || die "Wine registry is missing: $reg_file"
  case "$renderer" in
    gl|vulkan) ;;
    *) die "unsupported WineD3D renderer: $renderer" ;;
  esac
  count="$(LC_ALL=C /usr/bin/grep -Ec '^"renderer"="(gl|vulkan)"$' "$reg_file")"
  [[ "$count" == 1 ]] || die 'expected exactly one WineD3D renderer registry value'
  /usr/bin/sed -i '' -E "s/^\"renderer\"=\"(gl|vulkan)\"$/\"renderer\"=\"$renderer\"/" "$reg_file"
  LC_ALL=C /usr/bin/grep -qx "\"renderer\"=\"$renderer\"" "$reg_file" || die 'failed to update the WineD3D renderer registry value'
}

set_dll_override() {
  local dll="$1"
  local value="$2"
  local count
  [[ -f "$reg_file" ]] || die "Wine registry is missing: $reg_file"
  count="$(LC_ALL=C /usr/bin/grep -Ec "^\"$dll\"=" "$reg_file")"
  [[ "$count" == 1 ]] || die "expected exactly one $dll DLL override"
  /usr/bin/sed -i '' -E "s|^\"$dll\"=.*$|\"$dll\"=\"$value\"|" "$reg_file"
  LC_ALL=C /usr/bin/grep -Fqx "\"$dll\"=\"$value\"" "$reg_file" || die "failed to set the $dll DLL override"
}

select_local_dxvk() {
  set_dll_override d3d9 builtin
  set_dll_override d3d10core 'native,builtin'
  set_dll_override d3d11 'native,builtin'
  set_dll_override dxgi builtin
}

select_builtin_d3d11() {
  set_dll_override d3d10core builtin
  set_dll_override d3d11 builtin
  set_dll_override dxgi builtin
}

snapshot_dxmt_engine() {
  local temp arch dll windows_dir
  if [[ -f "$dxmt_stable_dir/complete" ]]; then
    return 0
  fi
  [[ ! -e "$dxmt_stable_dir" ]] || die 'incomplete DXMT engine snapshot exists; inspect it before continuing'
  temp="$(mktemp -d "$lab_dir/dxmt-engine-stable.tmp.XXXXXX")"
  for arch in i386-windows x86_64-windows; do
    mkdir -p "$temp/wine/$arch"
    for dll in d3d10core.dll d3d11.dll dxgi.dll winemetal.dll; do
      [[ -f "$wine_root/lib/wine/$arch/$dll" ]] || die "missing original Wine file: $arch/$dll"
      cp -p "$wine_root/lib/wine/$arch/$dll" "$temp/wine/$arch/$dll"
    done
  done
  for windows_dir in syswow64 system32; do
    mkdir -p "$temp/prefix/$windows_dir"
    for dll in d3d10core.dll d3d11.dll dxgi.dll winemetal.dll; do
      [[ -f "$prefix_root/$windows_dir/$dll" ]] || die "missing original prefix file: $windows_dir/$dll"
      cp -p "$prefix_root/$windows_dir/$dll" "$temp/prefix/$windows_dir/$dll"
    done
  done
  mkdir -p "$temp/wine/x86_64-unix"
  if [[ -f "$wine_root/lib/wine/x86_64-unix/winemetal.so" ]]; then
    cp -p "$wine_root/lib/wine/x86_64-unix/winemetal.so" "$temp/wine/x86_64-unix/winemetal.so"
  else
    : > "$temp/winemetal-so-was-absent"
  fi
  : > "$temp/complete"
  mv "$temp" "$dxmt_stable_dir"
  print -- 'Captured the isolated Wine engine and prefix files needed for a full DXMT rollback.'
}

restore_dxmt_engine() {
  local arch dll windows_dir
  [[ -f "$dxmt_stable_dir/complete" ]] || return 0
  for arch in i386-windows x86_64-windows; do
    for dll in d3d10core.dll d3d11.dll dxgi.dll winemetal.dll; do
      cp -p "$dxmt_stable_dir/wine/$arch/$dll" "$wine_root/lib/wine/$arch/$dll"
    done
  done
  for windows_dir in syswow64 system32; do
    for dll in d3d10core.dll d3d11.dll dxgi.dll winemetal.dll; do
      cp -p "$dxmt_stable_dir/prefix/$windows_dir/$dll" "$prefix_root/$windows_dir/$dll"
    done
  done
  if [[ -f "$dxmt_stable_dir/winemetal-so-was-absent" ]]; then
    rm -f "$wine_root/lib/wine/x86_64-unix/winemetal.so"
  else
    cp -p "$dxmt_stable_dir/wine/x86_64-unix/winemetal.so" "$wine_root/lib/wine/x86_64-unix/winemetal.so"
  fi
  select_local_dxvk
}

install_dxmt_engine() {
  local arch dll
  [[ -f "$dxmt_source/x86_64-unix/winemetal.so" ]] || die 'DXMT native Metal backend is missing'
  for arch in i386-windows x86_64-windows; do
    for dll in d3d10core.dll d3d11.dll dxgi.dll winemetal.dll; do
      [[ -f "$dxmt_source/$arch/$dll" ]] || die "DXMT file is missing: $arch/$dll"
    done
  done
  snapshot_dxmt_engine
  cp -p "$dxmt_source/x86_64-unix/winemetal.so" "$wine_root/lib/wine/x86_64-unix/winemetal.so"
  for dll in d3d10core.dll d3d11.dll dxgi.dll winemetal.dll; do
    cp -p "$dxmt_source/i386-windows/$dll" "$wine_root/lib/wine/i386-windows/$dll"
    cp -p "$dxmt_source/i386-windows/$dll" "$prefix_root/syswow64/$dll"
    cp -p "$dxmt_source/x86_64-windows/$dll" "$wine_root/lib/wine/x86_64-windows/$dll"
    cp -p "$dxmt_source/x86_64-windows/$dll" "$prefix_root/system32/$dll"
  done
  select_builtin_d3d11
}

install_stable_dxvk() {
  cp -p "$stable_dir/d3d10core.dll" "$game_dir/d3d10core.dll"
  cp -p "$stable_dir/d3d11.dll" "$game_dir/d3d11.dll"
  cp -p "$stable_dir/dxvk.conf" "$game_dir/dxvk.conf"
}

apply_stable() {
  local name
  restore_dxmt_engine
  for name in DDraw.dll D3DImm.dll D3D8.dll d3d10core.dll d3d11.dll dgVoodoo.conf dxvk.conf; do
    cp -p "$stable_dir/$name" "$game_dir/$name"
  done
  select_local_dxvk
  set_wined3d_renderer gl
}

apply_dgvoodoo_255() {
  local config="$1"
  local source="$candidates/dgvoodoo-2.55/unpacked/MS"
  [[ -f "$source/DDraw.dll" && -f "$source/D3DImm.dll" && -f "$source/D3D8.dll" ]] || die 'dgVoodoo 2.55 files are incomplete'
  [[ -f "$config" ]] || die "missing dgVoodoo config: $config"
  cp -p "$source/DDraw.dll" "$game_dir/DDraw.dll"
  cp -p "$source/D3DImm.dll" "$game_dir/D3DImm.dll"
  cp -p "$source/D3D8.dll" "$game_dir/D3D8.dll"
  cp -p "$config" "$game_dir/dgVoodoo.conf"
  restore_dxmt_engine
  install_stable_dxvk
  select_local_dxvk
  set_wined3d_renderer gl
}

apply_dgvoodoo_254() {
  local config="$1"
  local source="$candidates/dgvoodoo-2.54/unpacked/MS"
  [[ -f "$source/DDraw.dll" && -f "$source/D3DImm.dll" && -f "$source/D3D8.dll" ]] || die 'dgVoodoo 2.54 files are incomplete'
  [[ -f "$config" ]] || die "missing dgVoodoo config: $config"
  cp -p "$source/DDraw.dll" "$game_dir/DDraw.dll"
  cp -p "$source/D3DImm.dll" "$game_dir/D3DImm.dll"
  cp -p "$source/D3D8.dll" "$game_dir/D3D8.dll"
  cp -p "$config" "$game_dir/dgVoodoo.conf"
  restore_dxmt_engine
  install_stable_dxvk
  select_local_dxvk
  set_wined3d_renderer gl
}

apply_dgvoodoo_287() {
  local config="$1"
  local source="$candidates/dgvoodoo-2.87.3/unpacked/MS/x86"
  [[ -f "$source/DDraw.dll" && -f "$source/D3DImm.dll" && -f "$source/D3D8.dll" ]] || die 'dgVoodoo 2.87.3 files are incomplete'
  [[ -f "$config" ]] || die "missing dgVoodoo config: $config"
  cp -p "$source/DDraw.dll" "$game_dir/DDraw.dll"
  cp -p "$source/D3DImm.dll" "$game_dir/D3DImm.dll"
  cp -p "$source/D3D8.dll" "$game_dir/D3D8.dll"
  cp -p "$config" "$game_dir/dgVoodoo.conf"
  restore_dxmt_engine
  install_stable_dxvk
  select_local_dxvk
  set_wined3d_renderer gl
}

apply_dgvoodoo_wined3d_vulkan() {
  local version="$1"
  local config source
  case "$version" in
    253)
      source="$stable_dir"
      config="$stable_dir/dgVoodoo.conf"
      ;;
    255)
      source="$candidates/dgvoodoo-2.55/unpacked/MS"
      config="$candidates/dgvoodoo-2.55/dgVoodoo.ds1-baseline.conf"
      ;;
    287)
      source="$candidates/dgvoodoo-2.87.3/unpacked/MS/x86"
      config="$candidates/dgvoodoo-2.87.3/dgVoodoo.ds1-baseline.conf"
      ;;
    *) die "unsupported dgVoodoo version for WineD3D Vulkan: $version" ;;
  esac
  [[ -f "$source/DDraw.dll" && -f "$source/D3DImm.dll" && -f "$source/D3D8.dll" ]] || die "dgVoodoo $version files are incomplete"
  [[ -f "$config" ]] || die "missing dgVoodoo config: $config"
  cp -p "$source/DDraw.dll" "$game_dir/DDraw.dll"
  cp -p "$source/D3DImm.dll" "$game_dir/D3DImm.dll"
  cp -p "$source/D3D8.dll" "$game_dir/D3D8.dll"
  cp -p "$config" "$game_dir/dgVoodoo.conf"
  restore_dxmt_engine
  select_local_dxvk
  set_wined3d_renderer vulkan
}

apply_dgvoodoo_dxmt() {
  local version="$1"
  local config source
  case "$version" in
    253)
      source="$stable_dir"
      config="$stable_dir/dgVoodoo.conf"
      ;;
    255)
      source="$candidates/dgvoodoo-2.55/unpacked/MS"
      config="$candidates/dgvoodoo-2.55/dgVoodoo.ds1-baseline.conf"
      ;;
    287)
      source="$candidates/dgvoodoo-2.87.3/unpacked/MS/x86"
      config="$candidates/dgvoodoo-2.87.3/dgVoodoo.ds1-baseline.conf"
      ;;
    *) die "unsupported dgVoodoo version for DXMT: $version" ;;
  esac
  [[ -f "$source/DDraw.dll" && -f "$source/D3DImm.dll" && -f "$source/D3D8.dll" ]] || die "dgVoodoo $version files are incomplete"
  [[ -f "$config" ]] || die "missing dgVoodoo config: $config"
  cp -p "$source/DDraw.dll" "$game_dir/DDraw.dll"
  cp -p "$source/D3DImm.dll" "$game_dir/D3DImm.dll"
  cp -p "$source/D3D8.dll" "$game_dir/D3D8.dll"
  cp -p "$config" "$game_dir/dgVoodoo.conf"
  install_dxmt_engine
  set_wined3d_renderer gl
}

apply_dxwrapper() {
  local config="$1"
  local source="$candidates/dxwrapper-v1.7.8400.25/dx7-games"
  [[ -f "$source/ddraw.dll" && -f "$source/dxwrapper.dll" ]] || die 'dxwrapper files are incomplete'
  [[ -f "$config" ]] || die "missing dxwrapper config: $config"
  cp -p "$source/ddraw.dll" "$game_dir/DDraw.dll"
  cp -p "$source/dxwrapper.dll" "$game_dir/dxwrapper.dll"
  cp -p "$config" "$game_dir/dxwrapper.ini"
  restore_dxmt_engine
  select_local_dxvk
  set_wined3d_renderer gl
}

apply_dxwrapper_sarek() {
  local dxwrapper_config="$1"
  local dxvk_config="$2"
  local dxwrapper_source="$candidates/dxwrapper-v1.7.8400.25/dx7-games"
  local sarek_source="$candidates/dxvk-sarek-v1.12.0/unpacked/dxvk-sarek-dyasync-v1.12.0/x32"
  [[ -f "$dxwrapper_source/ddraw.dll" && -f "$dxwrapper_source/dxwrapper.dll" ]] || die 'dxwrapper files are incomplete'
  [[ -f "$sarek_source/d3d9.dll" ]] || die 'DXVK-Sarek D3D9 file is missing'
  [[ -f "$dxwrapper_config" ]] || die "missing dxwrapper config: $dxwrapper_config"
  [[ -f "$dxvk_config" ]] || die "missing DXVK-Sarek config: $dxvk_config"
  restore_dxmt_engine
  cp -p "$dxwrapper_source/ddraw.dll" "$game_dir/DDraw.dll"
  cp -p "$dxwrapper_source/dxwrapper.dll" "$game_dir/dxwrapper.dll"
  cp -p "$dxwrapper_config" "$game_dir/dxwrapper.ini"
  cp -p "$sarek_source/d3d9.dll" "$game_dir/d3d9.dll"
  cp -p "$dxvk_config" "$game_dir/dxvk.conf"
  set_dll_override ddraw 'native,builtin'
  set_dll_override d3d9 'native,builtin'
  set_wined3d_renderer gl
}

apply_sarek_d7() {
  local config="$1"
  local source="$candidates/dxvk-sarek-v1.12.0/unpacked/dxvk-sarek-dyasync-v1.12.0/x32"
  [[ -f "$source/ddraw.dll" && -f "$source/d3d9.dll" ]] || die 'DXVK-Sarek D7VK files are incomplete'
  [[ -f "$config" ]] || die "missing DXVK-Sarek config: $config"
  restore_dxmt_engine
  cp -p "$source/ddraw.dll" "$game_dir/DDraw.dll"
  cp -p "$source/d3d9.dll" "$game_dir/d3d9.dll"
  cp -p "$config" "$game_dir/dxvk.conf"
  set_dll_override ddraw 'native,builtin'
  set_dll_override d3d9 'native,builtin'
  set_wined3d_renderer gl
}

apply_dxgl() {
  local config="$1"
  local source="$candidates/dxgl-0.5.27/unpacked/ddraw.dll"
  [[ -f "$source" ]] || die 'DXGL 32-bit DirectDraw file is missing'
  [[ -f "$config" ]] || die "missing DXGL config: $config"
  restore_dxmt_engine
  cp -p "$source" "$game_dir/DDraw.dll"
  cp -p "$config" "$game_dir/dxgl.ini"
  set_dll_override ddraw 'native,builtin'
  set_dll_override d3d9 builtin
  select_builtin_d3d11
  set_wined3d_renderer gl
}

apply_d7vk2() {
  local config="$1"
  local source="$candidates/d7vk-v2.0/unpacked/d7vk-v2.0/x32/ddraw.dll"
  local mvk_target="$test_app/Contents/Frameworks/libMoltenVK.dylib"
  local mvk_candidate="$candidates/moltenvk-1.4.1/unpacked/libMoltenVK.dylib"
  [[ -f "$source" ]] || die 'D7VK 2.0 32-bit DirectDraw file is missing'
  [[ -f "$config" ]] || die "missing D7VK 2.0 config: $config"
  [[ -f "$mvk_target" && -f "$mvk_candidate" ]] || die 'MoltenVK files for D7VK 2.0 are incomplete'
  cmp -s "$mvk_target" "$mvk_candidate" || \
    die 'D7VK 2.0 requires the staged MoltenVK 1.4.1 profile; run moltenvk-lab.sh mvk141 first'
  restore_dxmt_engine
  cp -p "$source" "$game_dir/DDraw.dll"
  cp -p "$config" "$game_dir/dxvk.conf"
  set_dll_override ddraw 'native,builtin'
  set_dll_override d3d9 builtin
  select_builtin_d3d11
  set_wined3d_renderer gl
}

preflight_profile() {
  local profile="$1"
  local mvk_target="$test_app/Contents/Frameworks/libMoltenVK.dylib"
  local mvk_candidate="$candidates/moltenvk-1.4.1/unpacked/libMoltenVK.dylib"
  local plist="$test_app/Contents/Info.plist"
  case "$profile" in
    d7vk2-baseline|d7vk2-forced-vsync)
      [[ -f "$mvk_target" && -f "$mvk_candidate" ]] || \
        die 'MoltenVK files for D7VK 2.0 are incomplete'
      cmp -s "$mvk_target" "$mvk_candidate" || \
        die 'D7VK 2.0 requires the staged MoltenVK 1.4.1 profile; run moltenvk-lab.sh mvk141 first'
      [[ "$(/usr/libexec/PlistBuddy -c 'Print :MOLTENVKCX' "$plist")" == 0 ]] || \
        die 'D7VK 2.0 requires a mvk141 runtime profile so Wine loads the staged stock MoltenVK'
      ;;
  esac
}

show_status() {
  local name
  print -- "Isolated game directory: $game_dir"
  for name in "${managed_files[@]}"; do
    if [[ -e "$game_dir/$name" ]]; then
      stat -f '%N | %z bytes | %Sm' -t '%Y-%m-%d %H:%M:%S' "$game_dir/$name"
    fi
  done
}

usage() {
  print -- 'Usage: renderer-lab.sh <status|stable|dg254-baseline|dg254-roaming-cpl|dg255-baseline|dg255-fast|dg255-ti4800|dg255-ti4800-fast|dg287-baseline|dg287-fast|dg287-batched|dg287-batched-fast|dg287-d3d12|dg253-wined3d-vulkan|dg255-wined3d-vulkan|dg287-wined3d-vulkan|dg253-dxmt|dg255-dxmt|dg287-dxmt|sarek-baseline|sarek-vsync-no-limit|sarek-no-dyasync|d7vk2-baseline|d7vk2-forced-vsync|dxw-baseline|dxw-frameskip|dxw-qpc|dxw-sarek-baseline|dxw-sarek-frameskip|dxw-sarek-vsync-no-limit|dxgl-baseline|dxgl-forced-vsync>'
}

require_layout

case "${1:-}" in
  status)
    show_status
    ;;
  stable|dg254-baseline|dg254-roaming-cpl|dg255-baseline|dg255-fast|dg255-ti4800|dg255-ti4800-fast|dg287-baseline|dg287-fast|dg287-batched|dg287-batched-fast|dg287-d3d12|dg253-wined3d-vulkan|dg255-wined3d-vulkan|dg287-wined3d-vulkan|dg253-dxmt|dg255-dxmt|dg287-dxmt|sarek-baseline|sarek-vsync-no-limit|sarek-no-dyasync|d7vk2-baseline|d7vk2-forced-vsync|dxw-baseline|dxw-frameskip|dxw-qpc|dxw-sarek-baseline|dxw-sarek-frameskip|dxw-sarek-vsync-no-limit|dxgl-baseline|dxgl-forced-vsync)
    require_idle_game
    preflight_profile "$1"
    snapshot_stable
    archive_current
    case "$1" in
      stable)
        apply_stable
        ;;
      dg254-baseline)
        apply_dgvoodoo_254 "$stable_dir/dgVoodoo.conf"
        ;;
      dg254-roaming-cpl)
        apply_dgvoodoo_254 "$candidates/dgvoodoo-2.54/dgVoodoo.roaming-cpl.conf"
        ;;
      dg255-baseline)
        apply_dgvoodoo_255 "$candidates/dgvoodoo-2.55/dgVoodoo.ds1-baseline.conf"
        ;;
      dg255-fast)
        apply_dgvoodoo_255 "$candidates/dgvoodoo-2.55/dgVoodoo.ds1-fast-video-memory.conf"
        ;;
      dg255-ti4800)
        apply_dgvoodoo_255 "$candidates/dgvoodoo-2.55/dgVoodoo.ds1-ti4800.conf"
        ;;
      dg255-ti4800-fast)
        apply_dgvoodoo_255 "$candidates/dgvoodoo-2.55/dgVoodoo.ds1-ti4800-fast.conf"
        ;;
      dg287-baseline)
        apply_dgvoodoo_287 "$candidates/dgvoodoo-2.87.3/dgVoodoo.ds1-baseline.conf"
        ;;
      dg287-fast)
        apply_dgvoodoo_287 "$candidates/dgvoodoo-2.87.3/dgVoodoo.ds1-fast-video-memory.conf"
        ;;
      dg287-batched)
        apply_dgvoodoo_287 "$candidates/dgvoodoo-2.87.3/dgVoodoo.ds1-batched.conf"
        ;;
      dg287-batched-fast)
        apply_dgvoodoo_287 "$candidates/dgvoodoo-2.87.3/dgVoodoo.ds1-batched-fast.conf"
        ;;
      dg287-d3d12)
        apply_dgvoodoo_287 "$candidates/dgvoodoo-2.87.3/dgVoodoo.ds1-d3d12.conf"
        ;;
      dg253-wined3d-vulkan)
        apply_dgvoodoo_wined3d_vulkan 253
        ;;
      dg255-wined3d-vulkan)
        apply_dgvoodoo_wined3d_vulkan 255
        ;;
      dg287-wined3d-vulkan)
        apply_dgvoodoo_wined3d_vulkan 287
        ;;
      dg253-dxmt)
        apply_dgvoodoo_dxmt 253
        ;;
      dg255-dxmt)
        apply_dgvoodoo_dxmt 255
        ;;
      dg287-dxmt)
        apply_dgvoodoo_dxmt 287
        ;;
      sarek-baseline)
        apply_sarek_d7 "$candidates/dxvk-sarek-v1.12.0/dxvk.ds1-baseline.conf"
        ;;
      sarek-vsync-no-limit)
        apply_sarek_d7 "$candidates/dxvk-sarek-v1.12.0/dxvk.ds1-vsync-no-limiter.conf"
        ;;
      sarek-no-dyasync)
        apply_sarek_d7 "$candidates/dxvk-sarek-v1.12.0/dxvk.ds1-no-dyasync.conf"
        ;;
      d7vk2-baseline)
        apply_d7vk2 "$candidates/d7vk-v2.0/dxvk.ds1-baseline.conf"
        ;;
      d7vk2-forced-vsync)
        apply_d7vk2 "$candidates/d7vk-v2.0/dxvk.ds1-forced-vsync.conf"
        ;;
      dxw-baseline)
        apply_dxwrapper "$candidates/dxwrapper-v1.7.8400.25/dxwrapper.ds1-baseline.ini"
        ;;
      dxw-frameskip)
        apply_dxwrapper "$candidates/dxwrapper-v1.7.8400.25/dxwrapper.ds1-vsync-frame-skip.ini"
        ;;
      dxw-qpc)
        apply_dxwrapper "$candidates/dxwrapper-v1.7.8400.25/dxwrapper.ds1-qpc-fix.ini"
        ;;
      dxw-sarek-baseline)
        apply_dxwrapper_sarek \
          "$candidates/dxwrapper-v1.7.8400.25/dxwrapper.ds1-baseline.ini" \
          "$candidates/dxvk-sarek-v1.12.0/dxvk.ds1-baseline.conf"
        ;;
      dxw-sarek-frameskip)
        apply_dxwrapper_sarek \
          "$candidates/dxwrapper-v1.7.8400.25/dxwrapper.ds1-vsync-frame-skip.ini" \
          "$candidates/dxvk-sarek-v1.12.0/dxvk.ds1-baseline.conf"
        ;;
      dxw-sarek-vsync-no-limit)
        apply_dxwrapper_sarek \
          "$candidates/dxwrapper-v1.7.8400.25/dxwrapper.ds1-baseline.ini" \
          "$candidates/dxvk-sarek-v1.12.0/dxvk.ds1-vsync-no-limiter.conf"
        ;;
      dxgl-baseline)
        apply_dxgl "$candidates/dxgl-0.5.27/dxgl.ds1-baseline.ini"
        ;;
      dxgl-forced-vsync)
        apply_dxgl "$candidates/dxgl-0.5.27/dxgl.ds1-forced-vsync.ini"
        ;;
    esac
    print -- "Applied renderer profile: $1"
    ;;
  *)
    usage
    exit 2
    ;;
esac

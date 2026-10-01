#!/bin/zsh

set -euo pipefail

workspace='$HOME/Documents/Dungeon Siege 1'
test_app='$HOME/Applications/Dungeon Siege Wine10 Test.app'
original_app='$HOME/Applications/Dungeon Siege.app'
catalog="$workspace/fps-test-catalog.tsv"
results="$workspace/fps-test-results.tsv"
active_test="$workspace/fps-test-active.txt"
mvk_target="$test_app/Contents/Frameworks/libMoltenVK.dylib"
mvk_bundled_reference="$original_app/Contents/Frameworks/libMoltenVK.dylib"

die() {
  print -u2 -- "fps-test: $*"
  exit 1
}

require_idle_game() {
  if ps -axo comm=,args= | grep -E '(^|[[:space:]\\/])DSLOA\.exe([[:space:]]|$)' >/dev/null; then
    die 'DSLOA.exe is running; quit the isolated test game before preparing another test'
  fi
}

lookup_test() {
  local test_id="$1"
  awk -F '\t' -v test_id="$test_id" '$1 == test_id { print; found++ } END { if (found != 1) exit 1 }' "$catalog" || \
    die "unknown or duplicate test id: $test_id"
}

profile_exists() {
  local script="$1"
  local profile="$2"
  local usage_text
  usage_text="$("$script" __fps_catalog_probe__ 2>&1 || true)"
  usage_text="${usage_text//</|}"
  usage_text="${usage_text//>/|}"
  [[ "$usage_text" == *"|$profile|"* ]] || \
    die "catalog profile '$profile' is not advertised by ${script:t}"
}

check_catalog() {
  local spec column script profile
  [[ "$(head -n 1 "$catalog")" == $'id\tmoltenvk\truntime\trenderer\tprefs\tresources\tdescription' ]] || \
    die 'catalog header is invalid'
  awk -F '\t' '
    NF != 7 { print "line " NR " has " NF " columns" > "/dev/stderr"; bad=1 }
    seen[$1]++ { print "duplicate id: " $1 > "/dev/stderr"; bad=1 }
    END { if (NR != 65) { print "expected 65 rows, found " NR > "/dev/stderr"; bad=1 }; exit bad }
  ' "$catalog" || die 'catalog structure is invalid'

  for spec in \
    '2:moltenvk-lab.sh' \
    '3:runtime-lab.sh' \
    '4:renderer-lab.sh' \
    '5:prefs-lab.sh' \
    '6:resources-lab.sh'; do
    column="${spec%%:*}"
    script="$workspace/${spec#*:}"
    [[ -x "$script" ]] || die "profile script is not executable: $script"
    while IFS= read -r profile; do
      profile_exists "$script" "$profile"
    done < <(awk -F '\t' -v column="$column" 'NR > 1 && $column != "-" { print $column }' "$catalog" | sort -u)
  done
  print -- 'Catalog check passed: 64 tests and all component profiles resolve.'
}

explain_test() {
  local row test_id mvk runtime renderer prefs resources description
  test_id="$1"
  row="$(lookup_test "$test_id")"
  IFS=$'\t' read -r test_id mvk runtime renderer prefs resources description <<< "$row"
  print -- "$test_id: $description"
  print -- '  First: restore clean renderer/runtime/preferences/resources baseline'
  [[ "$mvk" == '-' ]] || print -- "  MoltenVK: $mvk"
  [[ "$runtime" == '-' ]] || print -- "  Runtime: $runtime"
  [[ "$renderer" == '-' ]] || print -- "  Renderer: $renderer"
  [[ "$prefs" == '-' ]] || print -- "  Preferences: $prefs"
  [[ "$resources" == '-' ]] || print -- "  Resources: $resources"
}

show_doctor() {
  local verified_line
  local -a stale_helpers stuck_wine
  check_catalog
  verified_line="$("$workspace/profile-live.sh" status | tail -n 1)"
  stale_helpers=(${(f)"$(ps -axo pid=,ppid=,stat=,comm=,args= | \
    awk '$2 == 1 && $4 == "start.exe" && $5 == "start.exe" && $6 == "/exec" && $7 == "DSLOA.exe" { print $1 }')"})
  stuck_wine=(${(f)"$(ps -axo pid=,stat=,args= | \
    awk -v test_app="$test_app" '$2 ~ /U/ && index($0, test_app) { print $1 }')"})

  print -- "$verified_line"
  print -- "Orphaned DSLOA start helpers: ${#stale_helpers[@]}${stale_helpers:+ (${(j:, :)stale_helpers})}"
  print -- "Uninterruptible isolated-wrapper Wine helpers: ${#stuck_wine[@]}${stuck_wine:+ (${(j:, :)stuck_wine})}"
  if (( ${#stale_helpers[@]} > 0 )); then
    print -- 'Profile preparation is intentionally blocked until the stale helpers are cleared.'
  else
    print -- 'No stale start helper blocks profile preparation.'
  fi
}

reset_baseline() {
  if ! cmp -s "$mvk_target" "$mvk_bundled_reference"; then
    "$workspace/moltenvk-lab.sh" bundled
  fi
  "$workspace/renderer-lab.sh" stable
  "$workspace/runtime-lab.sh" production
  "$workspace/prefs-lab.sh" baseline
  if "$workspace/resources-lab.sh" status | grep -q '^disabled'; then
    "$workspace/resources-lab.sh" restore
  fi
}

prepare_test() {
  local row test_id mvk runtime renderer prefs resources description
  test_id="$1"
  row="$(lookup_test "$test_id")"
  IFS=$'\t' read -r test_id mvk runtime renderer prefs resources description <<< "$row"

  require_idle_game
  reset_baseline
  [[ "$mvk" == '-' ]] || "$workspace/moltenvk-lab.sh" "$mvk"
  [[ "$runtime" == '-' ]] || "$workspace/runtime-lab.sh" "$runtime"
  [[ "$renderer" == '-' ]] || "$workspace/renderer-lab.sh" "$renderer"
  [[ "$prefs" == '-' ]] || "$workspace/prefs-lab.sh" "$prefs"
  [[ "$resources" == '-' ]] || "$workspace/resources-lab.sh" "$resources"
  print -- "$test_id" > "$active_test"
  print -- "Prepared $test_id: $description"
}

record_result() {
  local test_id="$1"
  local outcome="$2"
  local notes="${3:-}"
  local active=''
  [[ -f "$active_test" ]] && active="$(<"$active_test")"
  [[ "$active" == "$test_id" ]] || \
    die "active test is '${active:-none}', not '$test_id'"
  lookup_test "$test_id" >/dev/null
  if [[ ! -f "$results" ]]; then
    print -r -- $'timestamp\ttest_id\toutcome\tnotes' > "$results"
  fi
  printf '%s\t%s\t%s\t%s\n' "$(date '+%Y-%m-%dT%H:%M:%S%z')" "$test_id" "$outcome" "$notes" >> "$results"
  print -- "Recorded $test_id: $outcome"
}

show_next() {
  awk -F '\t' '
    NR == FNR { if (FNR > 1) done[$2] = 1; next }
    FNR == 1 { next }
    !($1 in done) { print $1 " | " $7; exit }
  ' "${results:-/dev/null}" "$catalog" 2>/dev/null || true
}

usage() {
  print -- 'Usage: fps-test.sh <check|doctor|catalog|explain TEST_ID|next|prepare TEST_ID|record TEST_ID OUTCOME [NOTES]|results|restore>'
}

[[ -f "$catalog" ]] || die "test catalog is missing: $catalog"

case "${1:-}" in
  check)
    check_catalog
    ;;
  doctor)
    show_doctor
    ;;
  catalog)
    column -s $'\t' -t "$catalog"
    ;;
  explain)
    [[ $# == 2 ]] || die 'explain requires one test id'
    explain_test "$2"
    ;;
  next)
    if [[ -f "$results" ]]; then
      show_next
    else
      awk -F '\t' 'FNR == 2 { print $1 " | " $7 }' "$catalog"
    fi
    ;;
  prepare)
    [[ $# == 2 ]] || die 'prepare requires one test id'
    prepare_test "$2"
    ;;
  record)
    (( $# >= 3 && $# <= 4 )) || die 'record requires test id, outcome, and optional notes'
    record_result "$2" "$3" "${4:-}"
    ;;
  results)
    [[ -f "$results" ]] && column -s $'\t' -t "$results" || print -- 'No results recorded yet.'
    ;;
  restore)
    require_idle_game
    reset_baseline
    print -- '00-clean-baseline' > "$active_test"
    print -- 'Restored the clean isolated-wrapper baseline.'
    ;;
  *)
    usage
    exit 2
    ;;
esac

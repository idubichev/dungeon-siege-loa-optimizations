# Phase 4 CPU profiling and exact math work (2026-09-06)

All experiments use the isolated Profile Test wrapper. Original app/saves and production Wine10 Test/Optimized remain unchanged at the 15-patch release.

## Current best candidate
- `12-triangle/DSLOA.exe`: production 15 patches + native cursor with corrected R/B mapping + triangle SSE fast path. SHA a9bfa14550fac8bd4d06bd6bfdfe3865814e9a43e9eb8767d94372abf2ebe08a.
- Native cursor alone (phase3) removed per-pixel surface readback and reached ~94 FPS in lighter forest; slow view still below 90.
- `04-cursor-colors`: native cursor colour fix; gold sword verified by full-screen cursor capture. Forbidden-ring red still needs visual verification. Handles cache as before; unsupported images fall back to software cursor.
- Triangle actual PE code passed 45,000 boolean/full-buffer comparisons, 9 x87 modes, degenerate geometry, vertical rays and aliases. `test-triangle-win32.py` manually maps test images and rebases legacy fixed-base absolute operands from a bounded 757-instruction CFG. Seven startup-initialized float constants copied from prior live image. Initial LoadLibrary test was invalid because the legacy EXE lacks relocations for its old math code. No live game memory writes.
- Triangle fixed forest HUD: 100.2,99.5,96.1,100.5,99.1 (mean 99.08); after screenshot92.4. Baseline matched procedure:98.1,94.1,94.7,89.5,86.2 (mean92.52). Promising ~7%, not yet proven stable90 across views.
- Future robustness: consider restricting triangle fast path to input magnitude <=1e10 and force SSE exception masks while restoring original MXCSR. Current fast path finite-input/alias/control guards, degenerate fallback. More extreme-range tests useful before delivery.

## Exact timers (instrumented, overhead present)
- `01-function-timer`: coarse forest root74% inclusive; skin26%; lighting4%.
- `02-render-timer/dense-active-2.json`: valid active combat, same private bookmark reset camera;75.5renderpasses/s. Exclusive wall:root19.83%, object6.29%, skin15.79%, lighting3.35%, draw67901a12.07%, draw677fac6.70%, visibility677e7e2.88%, intersection681f0f8.42%. Before/after PNGs alive.
- `10-triangle-timer/forest.json`: valid active capture;78.49renderpasses/s, skin16.41%exclusive, triangle7283435.70%, ray69395c4.91%, vertical693c451.82%, root45.47% (other work inclusive in root).
- `02/.../dense.json`, `dense-active.json`, `10/.../rotated.json` invalid paused/defeat captures; explicitly marked and excluded.

## Other candidates: NOT accepted
- `03-bounds` / `06-bounds-colors`: two per-vertex bounding min/max blocks69f6f3/69f81d use exact integer binary32 ordering. 90,000 bit-exact comparisons including NaNs/infinities/subnormals/signedzero/9controlmodes. In-game first92.44vsbaseline92.18 = no convincing gain.
- `08-matrix-skin`: batch large-weight matrix branch69f24a, 9,000 full loops bit-exact over9modes. First87.5vsbaseline92, repeat90.32vs92.52: no convincing gain. Not combined into best candidate.

## Reliable benchmark procedure
`benchmark.py EXE OUTDIR [rotation_ms] [clock_build_folder]` using lab .venv python.
- Exact Profile owning-prefix stop, copy EXE, direct launch.
- Wait for visually matched Continue menu (template from11-baseline-repeat/after.png); initial fixed2sec startup failed because click arrived before menu ready.11/13repeat results are MAIN MENU INVALID, marked.
- Click Continue via Ghostty/game-input-debug.sh, warm7sec, optional left-arrow hold, measure5HUD readings, captureafter, stop game immediately.
- Character takes damage in this private save. Never leave it playing while analyzing; this caused multiple discarded defeat captures. Existing `kp:esc` often misses; use `game-key.sh 53 100` (real key hold) if pausing needed.
- Private save CPU Bench.dssave verified/backed up `benchmark-save/`; Continue loads it. Camera resets on reload, so earlier dense camera is not retained in save.
- `game-key.sh` runs C CGEvent key-hold via Ghostty's existing Accessibility.123=left,650ms rotates ~45deg. Swift compilation failed due SDK module mismatch; C helper works. No permission changes.
- Debug input log `~/Documents/ds-input-debug.log` (only command trace).
- All FPS OCR must be visually checked; often invents leading1/missesdecimal.

## CPU frame cadence
`frame-clock.c` records QPC once per render-pass entry in 16384-slot ring. No per-object timing overhead. `build-frame-clock.py SOURCE_FOLDER OUTPUT_FOLDER`; reader uses manifestStateVA. `benchmark.py` optional clock folder runs reader concurrent with HUD capture.
-17-baseline-clock=04cursor+clock;18-triangle-clock=12triangle+clock.
-19-baseline-rotated (650msleft) valid active/alive:818intervals,81.898FPS mean,median11.6675ms,p9515.084ms,p9915.7848ms,worst16.5644ms,4.28%frames<=11.111ms. Not stable90. HUD OCR not yet corrected.
-20-triangle-rotated is the next comparison/current run. Inspect result and afterPNG before claims.
-CPU frame intervals are not GPU presentation timestamps. Keep that distinction.

## Source notes
triangle728343 normal case is Moller-Trumbore with epsilon1e-5 and barycentric tolerances+-0.001; complex degenerate branch retained original. Fast path uses SSE binary64 at x87PC53, rounding matched, float stores at original boundaries, fallback for otherPC/unmaskedx87/NaN/infinite/alias/nearzero determinant.
ray69395c mutates traversal scratch stack in object+1c; do not casually memoize complete function without proving geometry lifecycle and scratch postconditions.
No thermal/performance warning recorded by pmset. No OS/SIP/Rosetta modifications.

## Completed clock investigation and hardened candidate
- 20-triangle-rotated valid active gameplay: CPU cadence 89.228 FPS, median10.8072ms, p9514.3063ms, p9915.3659ms, worst17.5046ms;74.55% within11.111ms. HUDmean89.68. Baseline19 CPU81.898/HUD83.02. Improved, not stable90.
- Installed base DungeonSiege.exe is real1.11.1.1486 (July2 2003), LOA1.50.0.0056 (Oct16 2003). `21-binary-comparison/report.json` records hashes/imports/function signature matches. Main clock110instructions both: same overall QPC/timeGetTime design, baseSAHF branch sequences vs LOATEST AH sequences. Not bit-identical, not evidence of performance regression. No controlled same-content base-vs-LOA FPS comparison performed.
- `22-clock-profile` adds FXSAVE/FXRSTOR-safe timing around render pass, gameclock41b890 and CPUcalibration41f2a2. `23-clock-rotated/function-timing.json` valid alive capture: gameclock~760calls/s,1.25us/call,0.095%elapsed, render70.0%elapsed. CPUcalibration once atstartup0.1232ms,0calls in10sec gameplay. Zero instrumentationerrors/droppedframes. Timer is not material FPS cause in this workload. This excludes measured routines, not every possible pacing/cap issue.
- `24-triangle-safe/DSLOA.exe` is hardened candidate: abs(input)<=1e10 guard, explicit masked SSEexceptions and originalMXCSRrestore. SHA212b998eb2632120502918d148ad0d9f296821249f4d152aa9008d542dfb86d6. `triangle-safe.c`, `build-triangle-safe.py`, `test-triangle-safe-win32.py`.180,000 exactPE comparisons across9x87modes includingextremes/NaNs/infinities passed.
- `25-triangle-safe-clock` is diagnostic only; `26-triangle-safe-rotated` valid active:87.109FPSmean,p9514.5453,p9915.1771,worst18.6581;61.38%within90budget. HUD87.46. Still notstable90. Use uninstrumented24 fordelivery.
- Originaldeveloperpostmortem confirms node-space coordinate conversions and complexity already existed in2002, beforeLOA: https://www.gamedeveloper.com/design/postmortem-gas-powered-games-i-dungeon-siege-i- . No authoritativeLOA-specific regression proven.
- UI smoke currently27; Profile game paused for cursor/inventory/navigation checks. Production still15patch release untilexplicitinstallstep recordedbelow.

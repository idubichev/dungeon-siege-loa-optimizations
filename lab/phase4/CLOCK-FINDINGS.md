# Dungeon Siege LOA: executable and clock investigation

The measured clock routines do not explain the low frame rate. There are substantial costs in the game executable's rendering and geometry work, and changing that code has produced measurable gains. A specific LOA-versus-base performance regression has not been established.

## Direct measurements

Active combat in the isolated Profile Test wrapper, same private save and 650 ms camera rotation, 800 x 600 windowed. `23-clock-rotated/after.png` confirms the character was alive and gameplay active. Timing wrappers preserve floating-point/SSE state. Zero profiling errors or dropped records.

| Routine | Gameplay calls | Time |
|---|---:|---:|
| Game clock, `0x41b890` | About 760/second | About 1.25 microseconds each, 0.095% of elapsed time |
| CPU-cycle calibration, `0x41f2a2` | Zero during the 10-second capture | One startup call, 0.1232 milliseconds |
| Render pass, `0x676a6c` | About 84.6/second with instrumentation | 70.0% of elapsed time, including nested work and waits |

The render number is elapsed time inside that function, not a claim that 70% is Wine overhead or that 70% is pure CPU arithmetic. The timer measurement excludes these two routines as material bottlenecks in this scene; it does not exclude every possible frame-pacing issue elsewhere.

Evidence: `23-clock-rotated/function-timing.json`, `22-clock-profile/manifest.json`, `build-clock-profile.py`.

## Base game versus LOA binary

The installed base executable is Dungeon Siege 1.11.1.1486, July 2, 2003. LOA is 1.50.0.0056, October 16, 2003. Both are real game executables, not launch stubs.

The main clock has 110 instructions in both builds. Both use QueryPerformanceCounter, with timeGetTime fallback/correction. The base executable uses SAHF with conditional branches where LOA uses TEST AH with branches; addresses and branch displacements also differ. This is a largely shared timer design, not a discovered LOA timing-loop regression.

Matching instruction signatures also exist in several vector and animation routines. This is a partial binary comparison, not a complete semantic diff. A fair base-versus-LOA performance comparison still requires the same content, scene, settings and unmodified baseline binaries. Different campaigns or save versions are not a fair A/B test.

The original developer described coordinate-conversion overhead and engine complexity in December 2002, before LOA: [Bartosz Kijanka's Dungeon Siege postmortem](https://www.gamedeveloper.com/design/postmortem-gas-powered-games-i-dungeon-siege-i-).

Evidence: `21-binary-comparison/report.json`, `compare-binaries.py`, disassembly alongside the report.

## New executable optimization

The triangle-intersection replacement preserves the original fallback for unsupported floating-point modes, extreme/invalid inputs, aliases and degenerate geometry. The hardened version passed 180,000 exact boolean/full-buffer comparisons against the original PE code in nine x87 modes. It matches original rounding boundaries and does not use approximate reciprocal/square-root instructions.

In the matched lighter forest test, the initial triangle candidate increased displayed FPS from 92.52 to 99.08. In the harder rotated view, CPU render-pass cadence improved from 81.90 to 89.23 FPS; the hardened candidate repeated at 87.11 FPS. Its 95th-percentile interval was 14.55 ms, above the 11.11 ms required for stable 90 FPS. These are short workload-specific tests, not a sustained whole-game guarantee or GPU presentation trace.

The native cursor avoids the old software cursor's GPU surface readbacks, but current testing identified a cursor presentation problem after switching applications. Release installation is held until that issue is resolved. The existing optimized production launcher remains on the previous validated fifteen-optimization release as of this note.

Evidence: `24-triangle-safe/validation.json`, `14-baseline-fixed/result.json`, `16-triangle-fixed/result.json`, `19-baseline-rotated/frame-clock.json`, `20-triangle-rotated/frame-clock.json`, `26-triangle-safe-rotated/frame-clock.json`.

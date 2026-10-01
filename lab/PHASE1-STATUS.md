# Dungeon Siege: Legends of Aranna — tested optimization

Updated 6 September 2026. The original 90 FPS target has **not** been achieved. The finished local build improves the matched forest benchmark from **19.34 to 50.28 FPS**, approximately **2.60 times faster**. These are five visually checked HUD readings per configuration, not frame-time percentiles or a whole-game average.

## Launch and saves

Open `~/Applications/Dungeon Siege Optimized.app`. It launches the isolated Wine10 wrapper and automatically verifies and applies the eight improvements. Wait roughly 20 seconds for startup and patch application before choosing Continue. The helper logs to `~/Library/Application Support/Dungeon Siege Optimized/launch.log`.

The optimized game uses its own copied saves under `~/Library/Application Support/Dungeon Siege Optimized/user-data/Dungeon Siege LOA/Save`. Test-only progress was archived and the original starting saves recopied there after testing. Existing saves in `~/Documents/Dungeon Siege LOA` remain unchanged. Future progress in the optimized game stays in the private folder.

The original `~/Applications/Dungeon Siege.app` remains available for rollback. Close the optimized game before opening the original. The optimized launcher depends on `~/Applications/Dungeon Siege Wine10 Test.app` and its Application Support folder; retain both.

## What was verified

- Apple M4 MacBook Pro, 10 CPU / 10 GPU cores, 16 GB, macOS 15.0 (24A8332), on AC with Low Power Mode off.
- Installed game is the GOG DSLOA 1.50 build in a Wineskin wrapper. No commercial CrossOver.app was found in the usual locations. This work therefore uses the existing CrossOver-derived Wine setup.
- Actual game window: 800 by 600 client coordinates, with a 28-point title bar. macOS screenshots are Retina-sized. Configuration text says 1920 by 1080 in places; this is **not a verified 1080p benchmark**.
- Object detail remains 100%; shadows were already off. Audio is enabled in the game. Mac output remains muted at the user's request.
- Loaded the user's copied forest save, moved along the path, encountered enemies and exercised combat. The test character died during the encounter; this was not an engine crash. Restored the copied starting saves afterward. This is a short functional test, not a full campaign playthrough.
- Compared 32 backed-up original app/configuration files by SHA-256; all unchanged. Original user data including both saved games, preferences and keys also matches backup. A test-written shared crash log was archived here and its original restored.
- No OS or Rosetta system files were changed. Failed Wine11 experiments are retained under `rejected-runtimes/`, outside Applications.

## Strongest performance evidence

All rows below use the same running process, loaded save, camera, renderer and audio setting. The original routines were restored in memory, measured, then the validated hooks re-enabled and measured again. Source screenshots are retained in the named directories.

| State | Five visually verified FPS readings | Mean |
|---|---|---:|
| Original routines (`23-same-process-original-sound`) | 19.9, 18.9, 19.2, 19.8, 18.9 | 19.34 |
| Eight improvements (`24-same-process-optimized-sound`) | 50.8, 49.7, 50.2, 50.8, 49.9 | 50.28 |

Two cold launches with all eight improvements loaded the same forest at about 49–50 FPS; the final screenshot is `27-final-cold-launch-game.png`. Movement and enemy encounters in denser views showed roughly 44–46 FPS. Earlier lighter views reached around 60. None establishes sustained 90 FPS.

The screenshot OCR frequently misread digits: for example 50.8 became 156.8. The two canonical result.json files above contain visually corrected readings and preserve raw OCR values separately. Other experimental result.json files must not be treated as reviewed benchmark data. Menu screenshots, overlapping profiler measurements and black-screen renderer counters are not gameplay results.

## Kept renderer

Wine 10 Sikarugir, dgVoodoo 2.53 DirectDraw/Direct3D conversion, Gcenx DXVK-macOS 1.10.3 x32 D3D11/D3D10Core, and the wrapper's CodeWeavers MoltenVK path. Windowed flags: `nointro=true fullscreen=false nospacecheck=true bltonly=true`; esync/msync enabled; diagnostic logging off. A small DXVK FPS overlay remains available.

The largest gains came from reducing repeated legacy floating-point work in game and renderer routines. Simply choosing Metal did not remove that CPU work.

## Eight local improvements

The executable patch is in the isolated copy only. Seven further hooks are applied to that game process at launch. The launcher checks exact SHA-256 hashes and original instruction signatures; it refuses mismatched versions. Cache entries include the floating-point control mode and exact input bits, with original-code fallbacks.

| Routine | Implementation | Numerical comparisons |
|---|---|---:|
| Quaternion-vector rotation | SSE/SSE2 replacement; both 24- and 53-bit precision paths | 108,000 |
| dgVoodoo inverse matrices | Exact-input cache with original calculation on misses | 101,760 |
| dgVoodoo matrix multiply | SSE2 at 53-bit precision, original fallback | 75,000 |
| In-place quaternion interpolation | Exact-input cache | 50,000 |
| Vertex lighting | SSE/SSE2 replacement | 144,000 |
| Weighted vertex blend | SSE/SSE2 replacement | 108,000 |
| Four-argument quaternion interpolation | Exact-input cache | 90,000 |
| Strided vector transforms | SSE2 at 53-bit precision, original fallback | 72,000 |
| **Total** | **Byte-identical tested outputs** | **748,760** |

Tests cover rounding/precision modes, aliases and function-specific return/frame behavior. They compare against the extracted original routines. This is evidence for the tested inputs, not a proof over every possible input or every game area. The last vector-transform change provided a small gain in this scene; most of the improvement came from the earlier routines.

An important compatibility finding: enabling game audio changes the main thread's x87 control word from 24-bit to 53-bit precision. The first quaternion and lighting candidates consequently fell back to slow original code with audio enabled. The delivered versions handle both modes, and the final comparison includes audio.

Patched DSLOA.exe SHA-256: `61fb9d17369a878fd125a0ee937137a2ac7b53ebd93b5f968439a8de1c050102`.
Original DSLOA.exe SHA-256: `4e09ee31bea8f7e25387089ce584a84d96923af667c9e32933e96eb4fd8e9bbe`.
Sources, assembly, extracted routines, validation scripts and JSON results are retained in this directory. The authoritative deployed payload and exact hash manifest are in Application Support. The final manager scripts are also copied here.

## Alternatives investigated

| Candidate | Observed result / decision |
|---|---|
| Async cursor off; simplerender; dgVoodoo 2.54 and 2.55 variants | Approximately the original 19–21 FPS before targeted patches; no substantial gain |
| DXMT 0.80, direct D3D11-to-Metal | Works, but about 38–39 FPS with the then-current five improvements and audio, versus about 41–42 through DXVK; restored DXVK |
| DXVK-Sarek 1.12 D7VK path | Black menu; explicit `ddraw.forceProxiedPresent=True` did not fix it |
| D7VK 2.0 + MoltenVK 1.4.1 | DirectDraw enumeration failure even with explicit `ddraw.forceLegacyPresent=True`; restored bundled MoltenVK |
| Wine 11.16 | Tested in a separate cloned/upgraded prefix, retaining installation state; both the existing and Sarek D3D11 combinations failed graphics-device creation; rejected |
| System-wide rosettax87 patch | Source investigated; not applied. Targets different OS/Rosetta builds and requires privileged intervention |
| Native ARM64/FEX CrossOver preview | CodeWeavers states its native ABI path needs macOS 26.5; this Mac runs 15.0. No OS upgrade was performed |

Earlier July renderer, VSync, full-screen, resolution, power and wait-trace results are in `../../renderer-test-matrix.md`. They are historical, not fresh September measurements. In particular, the current result does not establish that every possible renderer/version combination has been exhausted.

## Reference and primary sources

The [supplied X post](https://x.com/marc_ibrahim/status/2096366866960621900?s=46) describes an Age of Empires IV Wine exception/code-cache improvement. The visible post did not provide a reusable source patch. Dungeon Siege's measured legacy math hotspots led to the game-local approach above.

- [DXMT 0.80 release](https://github.com/3Shain/dxmt/releases/tag/v0.80)
- [Gcenx Wine 11.16 release](https://github.com/Gcenx/macOS_Wine_builds/releases/tag/11.16). Downloaded archive SHA-256 verified against release metadata: `6f9af818b7af6001aeed7818cb32bf0155598c5ea4e3b33380a03cf814e033cd`.
- [CodeWeavers ARM64 preview requirements](https://www.codeweavers.com/blog/mjohnson/2026/7/31/crossover-preview-the-right-to-bear-arm64-on-mac)
- [Archived rosettax87 source](https://github.com/Lifeisawful/rosettax87)

Remaining boundary: 90 FPS is unmet. The result demonstrates substantial avoidable CPU translation cost, but does not prove that further work or an OS/runtime upgrade will reach 90. The delivered configuration is the fastest correctly rendering combination established in this investigation.

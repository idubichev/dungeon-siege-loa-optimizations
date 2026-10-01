# Dungeon Siege: Legends of Aranna — measured optimization

Updated 6 September 2026. The full-detail forest benchmark now runs around **about 70 FPS**, versus **50 FPS** after the first pass and **19 FPS** before targeted optimization. **Sustained 90+ FPS is not achieved.** Denser movement and combat still fall into the 40s–50s. These are visually reviewed FPS-overlay readings, not a whole-game average or frame-time percentiles.

## Launch, saves, and rollback

Open [Dungeon Siege Optimized.app](<~/Applications/Dungeon Siege Optimized.app>), then Continue. The launcher validates the installed game/renderer hashes and opens the isolated Wine10 wrapper. Patches load with the binaries; the old 20-second live-patching step is gone.

The optimized game uses copied saves in `~/Library/Application Support/Dungeon Siege Optimized/user-data/Dungeon Siege LOA/Save`. New progress stays there. The original game and `~/Documents/Dungeon Siege LOA` remain separate. The original 32 backed-up app/configuration files and seven user-data files were hash-checked unchanged during this pass. No system Rosetta files, SIP settings, developer authorization, or OS version were changed. Mac output remains muted as requested; game audio is enabled.

To return to the original, close the optimized game and open `~/Applications/Dungeon Siege.app`. The previous 50-FPS build is also retained as a complete rollback under `phase2/rollback/`. Keep the optimized wrapper and its Application Support folder together.

## Benchmark conditions and results

Apple M4 MacBook Pro, 10 CPU / 10 GPU cores, 16 GB, macOS 15.0 (24A8332), on AC, Low Power Mode off. Installed GOG DSLOA 1.50. No commercial CrossOver.app was found; this uses the existing CrossOver-derived Wineskin setup.

The tested window has an **800×600 client area**. Retina screenshots are larger; this is not a verified 1080p benchmark. Object detail is restored to **100%**, shadows remain at their original off setting, and the final renderer/quality settings match the first-pass forest comparison. The same copied save and original forward-facing camera are used for stationary comparisons.

| Test | Visually reviewed FPS | Mean |
|---|---|---:|
| Original routines, phase1 same-process A/B | 19.9, 18.9, 19.2, 19.8, 18.9 | 19.34 |
| First eight improvements, phase1 same-process A/B | 50.8, 49.7, 50.2, 50.8, 49.9 | 50.28 |
| Twelve static patches, full detail (`phase2/14-static-all`) | 60.0, 62.1, 61.8, 59.3, 60.1 | 60.66 |
| Matrix copies and lighting batch (`phase2/22-lighting-settled`) | 61.9, 64.5, 65.1, 63.8, 65.6 | 64.18 |
| Final fifteen patches (`phase2/27-raybox-full`) | 68.9, 68.8, 69.8, 71.1, 70.4 | 69.80 |
| Second final cold launch (`phase2/29-final-cold-two`) | 69.4, 69.7, 69.0, 68.4, 72.0 | 69.70 |

The first two rows are the strongest original-versus-patched same-process comparison. Later rows are separate cold launches, not a same-process A/B; the Windows thread-context sampler proved unreliable, so further live code swapping was discontinued. The final row is approximately 39% above the first-pass benchmark, and 3.6 times the original benchmark, under the stated scene conditions.

Movement into the denser enemy scene with the final build gave 63.9, 43.6, 47.4, 48.4, and 48.6 FPS while the view changed; a subsequent combat screenshot shows 53.3 FPS. The character moved, targeted and fought enemies without a visible rendering failure. These readings establish functional gameplay, not sustained 70 or 90 FPS in all scenes. Test progress was exited without saving.

A minimum-object-detail diagnostic reached 97.4–99.8 FPS, but removed many tree branches. Another 90+ result came from a different top-down camera. Neither is an equivalent-quality improvement, and neither is the delivered default.

Each canonical benchmark has source screenshots and `result.json`; corrected readings preserve the raw OCR separately. OCR often invents a leading 1 or mistakes 0 for 6. Unreviewed experimental files, startup/warmup samples, paused/menu counters, and overlapping profiler runs must not be treated as final benchmark evidence.

## Bottleneck and implementation

The major demonstrated cost is legacy floating-point work translated through Rosetta, spread across game geometry, animation, visibility and picking, plus dgVoodoo matrix operations. Native sampling also shows substantial time in Rosetta runtime helpers. A bounded Windows stack sample found D3D11 resource waits, including a DirectDraw/software-cursor path; this identifies a remaining cost but does not establish a precise percentage of frame time.

Fifteen entry points are active in the final build:

- Quaternion-vector rotation, weighted blending and vector transforms use checked SSE/SSE2 implementations.
- Two quaternion-interpolation routines and dgVoodoo inverse matrices cache exact inputs, including floating-point control mode; cache misses run original calculations.
- dgVoodoo matrix multiplication and two transpose/copy routines avoid legacy x87 work.
- Frustum checks, quaternion multiplication and orthonormalization use validated SSE2 paths.
- Vertex and lighting loops share floating-point setup across each batch.
- Ray/box intersection uses an SSE2 implementation with exact hit/output comparisons, and original-code fallback for unsupported precision, aliases and non-finite inputs.

Across the retained original and new numerical validation suites, **1,428,760 comparisons** matched the tested original outputs. This includes rounding/precision modes and function-specific aliases, return values, clipping masks, colors and floating-point-state restoration. It is strong test evidence, not a proof for every possible game state.

The game EXE has separate RX code and RW cache sections, with original and added base relocations. dgVoodoo 2.53 is packed: its wrapper entry first lets it unpack, validates the original instruction signatures, then installs the four renderer jumps during DLL initialization. No normal launch uses thread suspension or a Windows Python injector. Read-only inspection verified all fifteen loaded jumps and live cache counters.

Final files and hashes are pinned by `~/Library/Application Support/Dungeon Siege Optimized/static-manifest.json`; detailed hook addresses are in `static-patches.json`. The authoritative generated binaries are `phase2/static-raybox/` and the builder is `phase2/build-static-patches.py`. Older runtime installers are archived under Application Support `legacy-runtime-tools/` and must not be applied to this build.

## Renderer and rejected experiments

Kept: Wine 10 Sikarugir, dgVoodoo 2.53, Gcenx DXVK-macOS 1.10.3 x32, bundled CodeWeavers MoltenVK. Windowed flags: `nointro=true fullscreen=false nospacecheck=true bltonly=true`; esync/msync on, verbose logging off, DXVK FPS counter on.

The following did not establish a better stable result:

- Larger DXVK implicit-discard threshold, game VSync off, capped DXVK VSync-off run, asynchronous cursor off, and blit-only off: no meaningful sustained gain in their tested views. Defaults restored.
- An uncapped DXVK VSync-off startup crashed; the capped retry ran but did not improve FPS.
- An additional quaternion-to-matrix cache, consecutive-input SLERP cache and whole skinning-loop replacement passed numerical tests but offered little or no clear extra gain. They remain experiments, not active in the final build.
- Direct D3D11-to-Metal via DXMT 0.80 worked in the first pass but was slower than DXVK in the then-current five-patch comparison. It was not re-benchmarked with all fifteen patches.
- dgVoodoo 2.54/2.55 were slow before targeted patches; D7VK/Sarek alternatives had black-menu or device-enumeration failures. Wine 11.16 failed graphics-device creation in its separate cloned prefix.
- Latest rosettax87_jit source was inspected and its loader built, but required signatures were absent in this Mac's early macOS 15.0 runtime. Its runtime-library build also failed with the installed compiler. It was not injected; no privileged helper was installed.

The Windows Suspend/GetThreadContext sampler can terminate or freeze the game main thread in this Wine build, even when requesting only integer/control registers. The final launcher does not use it. Future profiling should begin with macOS sampling or carefully bounded static instrumentation, not those archived samplers.

## Sources and further limits

The [supplied X post](https://x.com/marc_ibrahim/status/2096366866960621900?s=46) concerned an Age of Empires IV exception/code-cache optimization; its visible content did not provide a reusable Dungeon Siege patch. Local measurements drove this implementation.

- [DXVK 1.10.3 configuration](https://github.com/doitsujin/dxvk/blob/v1.10.3/dxvk.conf) and [resource-mapping implementation](https://github.com/doitsujin/dxvk/blob/v1.10.3/src/d3d11/d3d11_context_imm.cpp)
- [DXMT 0.80](https://github.com/3Shain/dxmt/releases/tag/v0.80)
- [rosettax87_jit source](https://github.com/Lifeisawful/rosettax87_jit)
- [CodeWeavers native ARM64 preview requirements](https://www.codeweavers.com/blog/mjohnson/2026/7/31/crossover-preview-the-right-to-bear-arm64-on-mac), which specify a newer macOS than this installed 15.0 system

The untouched first-pass report is `PHASE1-STATUS.md`. July experiments are historical and are not fresh September evidence. This investigation has not exhausted every Wine/renderer/version combination, and does not establish that an OS/runtime upgrade would guarantee 90 FPS. The current result is a substantial measured improvement with the 90+ full-detail target still open.

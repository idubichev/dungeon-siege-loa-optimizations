# Dungeon Siege: Legends of Aranna — current installed build

Updated 7 September 2026. Open [Dungeon Siege Optimized.app](<~/Applications/Dungeon Siege Optimized.app>) and choose Continue. The current release adds batched object transforms and exact-input caching on top of the normal-loop optimization, native-cursor fix, earlier math improvements and OP mods. Object detail remains 100%; presentation is capped at 120 FPS. The latest fullscreen fix fits the actual Mac display, prevents the duplicate cursor and uses the user-confirmed 1280×800 UI layout with unchanged 1512×982 render/presentation output. [Fullscreen details and recovery](fullscreen-2026-09-07/STATUS.md).

## Latest object transform optimization

Translation, rotation and scale now produce the same rounded final matrix with one submission. A fixed cache reuses unchanged calculations. Two settled runs per build averaged **91.94 → 95.68 FPS (4.1%)**; individual new-build runs were 97.51 and 93.86 FPS. Walking was 84.31 → 85.62 FPS, with variable combat/path timing and worst frames 47.60 → 55.02 ms; no moving-stutter improvement is claimed. Sustained 110 FPS was not reached in this forest.

Validation includes 370,186 live original transform sequences, 36,000 kernel comparisons and 8,004 cache comparisons. [Exact math, all performance changes and evidence](phase9/MATH-AND-PERFORMANCE.md).

## Previous general CPU check and normal-loop optimization

Rendering accounted for about 66% of main-thread elapsed time in the diagnostic: skinning roughly 16%, drawing and its transform submissions roughly 18%. These measurements include probe overhead and waits; they are not GPU execution percentages. The native sample independently identified the indexed normal-transform loop as a hot path.

The new loop performs floating-point rounding setup once per group of normals, instead of once per normal. Across two settled dense-view runs per build, baseline 90.91/90.95 FPS became 92.12/95.32 FPS: about **3.1% faster on average**, with graphics settings unchanged. 14,400 full-loop comparisons matched every output bit across 12 floating-point modes, including arbitrary-bit inputs and duplicate indices.

Walking averages were broadly unchanged: baseline 82.23 FPS; candidate 81.80/83.63 FPS. Combat and paths vary, so these do not establish a moving-FPS gain. One 86.84 ms hitch remained in the repeat; smaller hitches are not fully resolved. [CPU breakdown, limits and rendering follow-up](phase8/CPU-CHECK.md).

The subsequent phase9 release implements the per-object transform change described above, with original-path fallbacks and the pinned renderer layout.

## Earlier cursor-fix evidence

The previous arrow patch bypassed cursor drawing too late: the old `RapiMouse.cpp` path still copied pixels to save and restore the software cursor background. Read-only profiling showed the input/display thread holding the shared renderer lock during the large hitches. The new native path exits before those copies, while retaining cursor coordination, window guards and the software fallback if native API initialization fails.

| Same programmed 35-second forest walk | Average CPU cadence | Worst frame | Frames above 80 ms |
|---|---:|---:|---:|
| Before cursor fix | 79.56 FPS | 118.82 ms | 3 |
| Cursor fix | 83.68 FPS | 53.17 ms | 0 |
| Cursor fix repeat | 82.49 FPS | 45.76 ms | 0 |

The large captured cursor-lock stalls were absent in both repeat walks. Smaller spikes remain. These tests use CPU render-entry timestamps, not GPU presentation timing, and combat/path timing varies. Stable 90 FPS everywhere and completely stutter-free travel are not claimed. Evidence and the call chain: [phase7/STATUS.md](phase7/STATUS.md).

Earlier phase6 math changes improved the same fixed demanding forest view from 57.62 FPS to 89.74 FPS. That stationary comparison is separate from the moving route above. SLERP passed 140,000 comparisons across x87 modes; bounds passed 50,000 exact buffer comparisons. Earlier triangle and other validated patches remain installed.

## Cursor, mods and saves

Held left/right clicks remain absolute and do not snap the visible pointer to the center. Middle-button camera movement hides the cursor, and release restores its position. Inventory and pause menus were checked on the unprofiled release. The native arrow replaces the game's contextual cursor artwork.

Two OP packages remain installed. Only the attack school actually used gains school XP. The main attribute grows at 1.35 and the other two at 1.0 (melee STR, ranged DEX, magic INT). Rare rolls are boosted 10x and unique rolls 5x within probability limits; vendor and consumable stock changes preserve stock budgets. Existing actor growth coefficients were migrated into the separate `Test OP.dssave`; a combat save comparison confirmed melee-only school XP and approximately 1.35:1:1 attribute growth. Vendor stock has package validation but has not been visually checked at a merchant. [Mod details and rollback](<~/Documents/Dungeon Siege 1/mods/2026-09-06/README.md>).

Original app and saves remain separate. The original `Test (0-04-34).dssave` is unchanged. The normal launcher was cold-started successfully with the new build and verified on `Test OP`, then closed at the user’s request; protected hashes still matched afterward. Normal progress belongs in `~/Library/Application Support/Dungeon Siege Optimized/user-data/Dungeon Siege LOA/Save`. Private invincible profiling saves are not installed in normal play. Removing a mod does not reverse earned attributes or serialized growth coefficients; load the preserved original save to return to its baseline.

## Release and operation

DSLOA.exe SHA-256: `3ff1a56264040d81c6b3e6a44b53301b0f246e0c1f0cdb40f13e7f0ed9e9b4e5`.

The support manifests pin five game/renderer binaries plus the fullscreen cursor presentation helper and record 23 jump hooks plus two direct cursor patches. No profiler, dynamic lock hook or cursor-focus dylib is part of normal startup. The original streaming sleep remains. DXVK now has `dxgi.maxFrameRate = 120`; other renderer options remain. The preceding release is backed up under `phase9/release-before`; older backups remain.

Historical performance tests use an 800×600 client area, 100% object detail and original shadows-off setting. Game audio remains enabled; Mac audio remains muted. No OS security or Rosetta settings changed. Keep the Wine10 Test wrapper: the optimized launcher uses its engine. Use the original `~/Applications/Dungeon Siege.app` for the separate original installation.

Ghidra's project and partial C++ reconstruction are under `phase7/ghidra-project`, `phase7/recovered-cpp` and `phase8/recovered-cpp`. Inferred names are labeled; these are analysis artifacts, not the original source. The additional length-math candidate and streaming-sleep experiment were not installed.

## Expanded inventory, 7 September

Zhixalom v3.2 LoA SinglePlayer installed: 242 grid squares. Current Testq save compatibility was verified privately by placing an item in the final square, saving, fully restarting and retrieving it. Original manual saves preserved; no XP/loot resource overlaps. Details: ~/Documents/Dungeon Siege 1/mods/2026-09-07-inventory/README.md

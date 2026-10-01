# Cursor-related renderer stalls: measured fix

Installed source: `22-native-fastpath/DSLOA.exe`, SHA-256 `3b222ce4f8214a182112ef65db869cfe1132f4b3b4ff80999eaefabeb704c919`.

## What caused the large captured hitches

The previous native-arrow patch replaced the final cursor drawing routine, but left the old software cursor's background surface copies active. Those copies could hold the graphics wrapper's shared critical section on the input/display thread, blocking the main game thread for roughly 100 ms.

The measured main-thread path was `0x477118` (game update) -> `0x59bfcd` (mood update) -> `0x65ecff` (fog distances) -> D3DImm `SetRenderState` -> critical-section wait. The wait could also occur in camera or drawing calls using the same lock; the fog arithmetic itself was not the problem.

`21-lock-owner-readonly` sampled the lock without modifying or suspending threads. Every captured fog stall over 60 ms coincided with owner thread 368 (the input/display thread), not worker 416 (streaming). The original software cursor path is `0x662403` -> `0x6629ba` -> `0x663289`. Ghidra shows DirectDraw Blt and Lock/Unlock copies in that last helper. A nearby original diagnostic string names `c:\DSX\GPG\LIB Projects\Rapi\RapiMouse.cpp`.

## Change

`native-cursor-fastpath.s` and `build-native-fastpath.py` add one jump at `0x662a12`. Original cursor event coordination and window guards still run. The new path updates the native arrow and exits before the software background copies. If native cursor initialization fails, it resumes the original software branch. Registers and floating-point state are preserved around the native call.

The earlier click fix, relative camera behavior, SLERP, mesh-bounds, triangle, skinning, lighting and other installed improvements remain. The original streaming sleep remains 100 ms; the length-math candidate is not included. Renderer DLLs, DXVK settings and normal saves were not changed by this release.

## Validation

In the detailed diagnostic walk, fog-update worst time dropped from 104.42 ms to 1.11 ms. The input/display thread no longer appeared as renderer-lock owner. Cursor surface-copy and resize helpers were not called during the measured interval after the bypass. One separate 67.93 ms game-update spike remained in that diagnostic run.

The subsequent tests used only a single render-entry timestamp, without the detailed wrappers or lock sampler:

| 35-second programmed walk | Average CPU frame cadence | p99 frame | Worst frame | Frames over 80 ms |
|---|---:|---:|---:|---:|
| Previous installed build | 79.56 FPS | 18.29 ms | 118.82 ms | 3 |
| Cursor copy bypass | 83.68 FPS | 17.35 ms | 53.17 ms | 0 |
| Cursor copy bypass repeat | 82.49 FPS | 17.87 ms | 45.76 ms | 0 |

Evidence: `25-walk-baseline`, `26-walk-fastpath`, `27-walk-fastpath-repeat`. Each starts from the same private invincible travel checkpoint and uses the same click sequence. Combat and path timing vary, so the small average-FPS difference is a limited comparison. These are CPU render-entry intervals, not GPU presentation measurements. Smaller spikes remain; this does not establish perfectly stutter-free travel or stable 90 FPS everywhere.

The unprofiled candidate passed held left/right clicks, absolute movement, hidden cursor during middle-button camera movement, pointer restoration after release, inventory and pause-menu checks (`28-cursor-validation`). Static validation checked all 17 EXE jump destinations, the original streaming delay, absence of the frame timer and preservation of the click patch. There are 21 installed jump hooks across the EXE and renderer plus one direct cursor patch.

## C++ analysis and rejected diagnostics

`ghidra-project/Siege` contains the original DSLOA program and an analysis-only unpacked DDraw image. `recovered-cpp` contains partial C++ decompilation with inferred class/method names explicitly labeled. These files are not original source or replacement implementations. Ghidra's calling conventions and parameter storage were retained.

Native macOS sampling attached successfully but added substantial overhead. D3DImm import timing confirmed the long critical-section waits. Broader DDraw import hooks caused private diagnostic crashes and were discarded; the successful ownership trace was read-only. No such hooks or samplers are installed in normal startup. Never use the old Windows Suspend/GetThreadContext sampler.

Reducing the streaming worker sleep to 1 ms did not remove the 100 ms waits and was rejected. The squared-length candidate passed exact numerical tests but was not promoted without a clean performance benefit.

## Installed state and rollback

Normal launcher: `~/Applications/Dungeon Siege Optimized.app`, backed by `Dungeon Siege Wine10 Test.app`. Installed hashes and hooks are in the support folder's `static-manifest.json` and `static-patches.json`; `installed-release.json` records this release. `release-before` contains the preceding executable and support files.

The normal launcher was cold-started successfully with the installed release, loaded `Test OP.dssave`, and was left paused. `29-normal-launch/final-verification.json` records the five binary hashes, two package hashes and protected-save checks. The normal Continue save remains `Test OP.dssave`. The original `Test (0-04-34).dssave` and other protected originals remain unchanged. Private invincible travel saves stay inside Profile Test. The OP packages and existing XP playtest evidence are documented in [the mod README](<~/Documents/Dungeon Siege 1/mods/2026-09-06/README.md>).

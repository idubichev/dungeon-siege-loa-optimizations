# Dungeon Siege LoA performance test matrix

Test target: the same in-game scene at 1920x1080 unless noted. Success requires materially better than the observed ~20 FPS while preserving a correct image.

## Fixed configuration

- LoA fix installed and verified.
- `bltonly=true` (GenesisFR poor-performance workaround).
- NVIDIA GeForce 8800 GTX Hardware TnL entry selected in DSVideoConfig.
- dgVoodoo 2.53 DirectDraw/D3D8/D3DImm files from the Steam recipe.
- Gcenx DXVK-macOS 1.10.3 x32 `d3d11.dll` and `d3d10core.dll`.
- VSync enabled unless a row says otherwise.

## Completed tests

| Renderer / variable | Result | Decision |
| --- | --- | --- |
| Wine built-in DirectDraw/OpenGL | Renders at ~20 FPS | Too slow |
| GOG DirectDraw wrapper + WineD3D D3D9 | Renders at ~20 FPS | Too slow |
| GOG DirectDraw wrapper + upstream DXVK D3D9 | Black screen; graphics pipeline compilation failures | Incompatible |
| dgVoodoo 2.79.3 + upstream DXVK D3D11/DXGI | DirectDraw enumeration fatal error | Incompatible |
| dgVoodoo 2.79.3 + WineD3D | DSVideoConfig crash | Incompatible |
| dgVoodoo 2.79.3 + Gcenx DXVK-macOS D3D11 | DirectDraw enumeration fatal error | Incompatible |
| dgVoodoo 2.53 + WineD3D | OpenGL buffer/FBO errors and access violation | Incompatible |
| dgVoodoo 2.53 + Gcenx DXVK-macOS D3D11 | Correct rendering, ~20 FPS | Stable baseline, too slow |
| dgVoodoo Virtual 3D 1024 MB vs GeForce4 Ti 4800 256 MB | Both ~20 FPS | GPU identity not limiting |
| dgVoodoo 59/60/120 Hz output | ~20 FPS | Refresh selection not limiting |
| VSync off | Still slow and visually terrible | Rejected; keep VSync on |
| `bltonly=false` | Worse | Rejected; keep `bltonly=true` |
| `maxfps=60` vs `maxfps=0` | Both ~20 FPS | Game limiter not limiting |
| 1280x720 game surface into 1920x1080 dgVoodoo output | Menu works; Continue gives black 3D scene | Incompatible resolution mismatch |
| True fullscreen at 1920x1080 | Crisp image, same ~20 FPS; host remains 3024x1964 | Window compositor not limiting |
| Wine 10.0 Sikarugir revision 3, windowed | Menu 145-200 FPS; loaded 3D scene ~20-23 FPS | Newer Wine alone does not fix gameplay |
| DXVK async disabled/enabled | No material change to the steady loaded-scene rate | Shader compilation is not the steady-state bottleneck |
| DXVK/Metal HUD profile | ~21-23 FPS, 423-537 draws, 5 submissions, GPU 6-7%, GPU time ~1.9 ms, present/frame time ~46-49 ms | CPU/translation bound, not fill-rate bound |
| Wine relay trace, two bounded 5-second slices | Main thread has no long `Sleep` or blocking wait; dgVoodoo DDraw worker signals at ~62.6 Hz | No 20 FPS Wine wait/timer cap found |
| Native macOS `sample` capture | Rosetta cannot unwind the 32-bit PE call stacks; nearly all samples collapse into Wine's syscall dispatcher/runtime | Module-level CPU percentages are not trustworthy; use the DXVK/Metal HUD and bounded relay results instead |
| Host power state | MacBook Pro is on AC power and both AC/battery profiles have Low Power Mode disabled | Power throttling is not the cause |

## Active test

- The isolated Wine 10 wrapper is stopped; no foreground app will be launched while the user is playing another game.
- A clean recommended-flags baseline is staged next, with diagnostic relay/module logging and the duplicate Metal HUD disabled; the DXVK HUD remains available for FPS measurement.
- `simplerender=true` follows as the first single-variable comparison. The option exists in `DSLOA.exe` and corresponds to the game's `simple_render` low-end rendering capability.
- The current save already has shadows disabled and object detail at 100%, so shadows cannot explain the 20 FPS result.
- The active `prefs.gas` has `priority_boost=false`. Static control-flow inspection confirms that `true` sets Dungeon Siege's `0x40000000` application flag, which reaches `SetPriorityClass` and requests either `ABOVE_NORMAL_PRIORITY_CLASS` or `HIGH_PRIORITY_CLASS`. Upstream Wine 10 only records that priority in wineserver and does not call the host's `setpriority`, so this is a cheap wrapper-specific check rather than an expected fix. A reversible A/B is staged in `prefs-lab.sh`.
- `sound_enabled=false` is already active, so the measured ~20 FPS is not explained by normal audio processing; the separate `nosound=true` launch flag is now a low-priority confirmation rather than a primary diagnostic.
- The wrapper contains both CodeWeavers-customized MoltenVK 1.2.5 and a separate stock MoltenVK build. Reversible selectors for each, plus stock-with-argument-buffers-disabled, passed a disposable plist test.

## Profiling conclusion

The reproducible loaded scene is bottlenecked on the single game/render thread crossing the legacy Direct3D 7 translation path. The GPU is mostly idle and changing window size, forced output resolution, fullscreen presentation, refresh rate, or emulated VRAM does not materially alter FPS. The remaining useful experiments either reduce legacy draw-call work in the game or replace the DirectDraw/Direct3D 7 translator.

The 70.082-second Wine relay trace also rules out a hidden game-loop sleep cap. Dungeon Siege's main thread made 31,972 `NtWaitForMultipleObjects` calls but spent only 203 ms total inside them, and made one 51 ms `Sleep` call. Recurring waits are therefore less than 0.3% of the capture; almost all frame time is active CPU-side work. Separate game-created worker threads do sleep repeatedly, but they are not the main/render thread.

Prepared but not installed:

- Official-version dgVoodoo 2.54 DLLs from an archived binary mirror, matching the Steam thread's highest-FPS result and retaining exact rollback.
- Official dgVoodoo 2.55, the nearest text-config successor to the working 2.53 build.
- Official dgVoodoo 2.87.3, forced to D3D11 for one bounded retry because its post-2.79 releases include relevant DDraw and CPU-side performance fixes.
- Official dxwrapper v1.7.8400.25, whose Dd7to9 path converts DirectDraw/Direct3D 1-7 to Direct3D 9.
- dxwrapper Dd7to9 paired with DXVK-Sarek's D3D9 backend, retaining a D3D7 -> D3D9 -> Vulkan path even if Sarek's own D7VK frontend cannot enumerate.
- Official DXMT v0.80 builtin release, with a verified 32-bit D3D11-to-Metal path and a byte-for-byte rollback profile for the isolated Wine engine.
- DXVK-Sarek v1.12 with its D7VK backport, a separate CPU-optimized D3D7-to-D3D9 frontend on a Vulkan 1.1/1.2 backend. Baseline and two single-variable profiles have verified rollback.
- DXGL 0.5.27, a portable DirectDraw/Direct3D-to-OpenGL frontend with app-driven and forced-VSync profiles.
- D7VK 2.0 with official MoltenVK 1.4.1 in the isolated wrapper's stock slot, enabling a current D3D7 -> DXVK 3.0.2 -> Vulkan 1.4 -> Metal path with exact framework rollback.
- A guarded native macOS sampler in `profile-live.sh`. It attaches only when exactly one `DSLOA.exe` process is verified by open files inside the isolated wrapper, then captures an eight-second host call tree without killing or controlling the game.
- A 64-row guarded benchmark catalog in `fps-test-catalog.tsv` with `fps-test.sh` baseline restoration, active-test tracking, and TSV result logging. It prepares settings only; game launch and the loaded-scene measurement remain explicit steps.

## Remaining high-value tests

1. Re-measure the stable renderer with only the four published launch flags (`nointro`, windowed, no space check, and `bltonly`), removing the diagnostic-only `always_active` and `fpslog` flags.
2. Test `asynccursor=false` alone. DSLOA exposes this compatibility option directly, and disabling the asynchronous software cursor is reported to improve frame rate at the cost of less responsive cursor motion; this also targets the non-zero macOS message-loop overhead seen in the relay trace.
3. Enable `priority_boost=true` alone. Reject it quickly if the wrapper behaves like upstream Wine 10 and FPS is unchanged.
4. `simplerender=true` alone, measured in the same save and camera position.
5. dgVoodoo 2.54 with the current known-good binary control-panel config. This exact version produced the Steam thread's 180–270 FPS report and its changelog includes lower resource use plus a revised GeForce4 profile.
6. dgVoodoo 2.54 with the preserved roaming control-panel config from the earlier Steam recipe attempt. It is byte-for-byte evidence from the second control-panel instance rather than a decoded reconstruction, so its first run may be fullscreen; restore immediately after measurement.
7. dgVoodoo 2.55 with a hand-authored text config. Start with the Steam recipe's `GeForce4 Ti 4800`, 256 MB, app-driven resolution/AA, and `FastVideoMemoryAccess=false`; then change only fast video-memory access. Retain the generic-card pair as a secondary A/B.
8. Bounded dgVoodoo 2.87.3 retry through D3D11. If it initializes, compare baseline, `FastVideoMemoryAccess`, and its documented `PrimarySurfaceBatchedUpdate` option, combining the latter two only if one helps independently. Give its separate D3D12/VKD3D profile one bounded initialization test even if D3D11 fails, because the output-device path is materially different; reject it immediately on a missing-feature/device error.
9. Replace DXVK/Vulkan/MoltenVK with the official DXMT v0.80 direct-Metal builtin, first behind dgVoodoo 2.53 and 2.55, then 2.87.3 only if step 8 enumerates. If any renders, A/B DXMT defaults, logging disabled, and its documented Metal 60 FPS frame pacing.
10. Replace dgVoodoo with DXVK-Sarek v1.12's D7VK frontend and Sarek D3D9 backend. Reject the branch immediately if MoltenVK device creation fails; otherwise compare baseline, forced VSync with Sarek's separate limiter disabled, and dyasync disabled.
11. Keep the working dgVoodoo 2.53 + Gcenx DXVK frontend fixed and compare the wrapper's bundled CodeWeavers MoltenVK, its bundled stock build, and official MoltenVK 1.4.1. The dedicated `mvk141-*` runtime profiles atomically set `MOLTENVKCX=0`, ensuring the replacement stock library is really loaded. On 1.4.1, test its default first, synchronous queue submission second, and asynchronous submission third. This isolates the Vulkan-to-Metal backend before changing the D3D frontend.
12. Give D7VK 2.0 with official MoltenVK 1.4.1 one bounded compatibility test. Its current DXVK 3.0.2 backend is materially newer than Sarek, but it hard-requires several features that bundled MoltenVK reports as unavailable; the renderer preflight rejects the test unless both the 1.4.1 library and its stock-library selector are active. Stop immediately on any missing-feature/device-creation error and restore the stable frontend and bundled MoltenVK.
13. Test one back buffer and the game's `buffers_frames=false`/`no_flip` capability combinations; the current NVIDIA profile uses two back buffers, `buffers_frames=true`, and `no_flip=true`. The same profile also enables a shadow render target and trilinear capability, so single-variable disable profiles are staged before the combined `render-min` profile.
14. Remove local DXVK and test dgVoodoo 2.53 and 2.55 through Wine 10's built-in WineD3D Vulkan backend, adding 2.87.3 only if it enumerates. The installed 32-bit `wined3d.dll` contains both OpenGL and Vulkan paths; the earlier WineD3D failure used the registry's explicit `renderer=gl` path.
15. dxwrapper Dd7to9 as a different Direct3D 7 translator. Start with WineD3D/D3D9; if it renders, A/B `DdrawAutoFrameSkip` and `FixPerfCounterUptime` separately, then replace only the D3D9 backend with Sarek and repeat the useful single-variable checks.
16. Give DXGL 0.5.27 one bounded baseline test through Wine OpenGL. It adds no scaling, postprocessing, AA, or dithering shader; force redraw VSync only if app-driven VSync is ignored on an otherwise correct image.
17. Wine 10 sync matrix: ESYNC only, MSYNC only if supported, both disabled; also remove `+loaddll` logging for the clean run.
18. If renderer-level changes fail, use `engine-lab.sh` to APFS-clone the clean isolated wrapper and activate its retained complete CrossOver 23.7.1 engine only in `Dungeon Siege CX23 Test.app`. Give that different runtime one bounded test, then A/B Wine 10 revision 3 against the supported Porting Kit Wine 10 revision 6 in another clone if needed. The supported Porting Kit CrossOver 24.0.7 engine follows only if both local engines remain slow. As a final external engine/backend branch, the current actual CrossOver 26.2 product exposes D3DMetal 3.0, a proprietary D3D11-to-Metal path absent from every local wrapper; give dgVoodoo-to-D3DMetal one bounded 32-bit compatibility test before ruling it out. Never replace the original Dungeon Siege app's engine or reuse the known-good isolated wrapper as an engine-swap target.
19. On any working MoltenVK path, A/B `MVK_CONFIG_SYNCHRONOUS_QUEUE_SUBMITS=1` versus `0`: official MoltenVK moves `vkQueueSubmit`/`vkQueuePresentKHR` processing from the calling thread to a priority-aware GCD queue when disabled, directly targeting the measured CPU/present bottleneck. If that helps, test its one-queue/no-explicit-semaphore style separately and then combined. With the bundled stock build, also test `MVK_CONFIG_USE_METAL_ARGUMENT_BUFFERS=0`; do not apply this branch to DXMT, which bypasses Vulkan. If FPS remains capped, use the diagnostic-only `mvk141-perf-60` and brief `mvk141-trace-calls` profiles to collect MoltenVK internal statistics and per-call timings in `LastRunWine.log`.
20. Diagnostic quality reductions only if needed: `diagnostic-bpp16`, `diagnostic-notextures`, and stepped object detail to measure draw-call and render-state scaling. `prefs-lab.sh` stages 75%, 50%, 25%, the engine's true minimum of 20%, and a 50% + priority-boost combination. The 16-bit and no-texture profiles are diagnostic only and can never become the sharp production profile.
21. If renderer and quality diagnostics remain flat, use `resources-lab.sh minimal` for one same-save comparison without the five optional `.dsres` packages. If and only if FPS improves, restore and disable each package individually to isolate the offender. The script snapshots and archives every managed file, targets only the isolated wrapper, and never removes core DS/LoA resources.
22. Pause the loaded game without changing the camera. Since `sound_enabled=false` was already active during the poor result, `nosound=true` is retained only as a low-priority confirmation.
23. D9MT remains an experimental last resort behind dxwrapper or D7VK. The current `dx9` branch is captured at commit `69361dff94c170a3de546e2b7fedefbc3e56fef7`, but its fork has no releases or CI artifacts and this Mac lacks Meson, MinGW/LLVM-MinGW, LLVM libraries, and the Metal compiler, so a local build is deferred behind every packaged path.
24. RDM host refresh at 60 Hz as a final external display diagnostic, with user control because it changes the whole display.

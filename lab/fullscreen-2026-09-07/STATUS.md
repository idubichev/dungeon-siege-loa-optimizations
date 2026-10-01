# Fullscreen correction — 7 September 2026

Normal launch: Dungeon Siege Optimized.app. Final game UI selection is 1280×800; no width/height arguments override the setting. The user confirmed this fixes physical mouse reach and text readability. dgVoodoo presentation is 1512×982, matching the current Mac display. The menu itself still uses its original 800×600 layout. The final game was left paused for the user.

## Corrections

- Removed the stale Wine Explorer Desktop=Default override pointing at a fictitious 1920×1080 desktop. This was producing a native game window wider/taller than the actual 1512×982 screen, cutting off the right and bottom edges. The profile and normal prefixes were corrected; no global macOS settings were changed permanently.
- Used dgVoodoo 2.53 Setup to select a display-sized 1512×982 output. All existing renderer DLLs remain byte-identical.
- DSLOA.exe: the two-byte conditional branch at VA 0x415d2b (file offset 89387) is replaced with NOPs. Fullscreen alone no longer forces relative mouse recentering. The explicit middle-button camera flag remains. These are the only two changed bytes compared with the previous release; all 23 performance/cursor hooks and the prior held-click patch remain intact.
- fullscreen-cursor.m / fullscreen-cursor.dylib: within the Wine process, substitute a transparent AppKit cursor only while the active key window is the display-sized Dungeon Siege window. dgVoodoo continues drawing the correctly scaled Win32 arrow. This prevents the extra unscaled Mac pointer. The ordinary cursor is restored on app switching. This uses cursor events and activation notifications, with no polling timer or profiler.
- The wrapper's CLI Custom Commands loads that private presentation helper. The support hash manifest pins it alongside the five existing game/renderer binaries.

EXE SHA-256: 3ff1a56264040d81c6b3e6a44b53301b0f246e0c1f0cdb40f13e7f0ed9e9b4e5

## Verification

Correction: earlier SetCursorPos checks did not prove physical pointer reach. The later user report exposed that limitation. A private 1280×800 UI trial was physically checked and explicitly confirmed by the user ("Hey you did it!!"). It was then applied in-game to production and persisted in both INIs. See ui-input/STATUS.md. Earlier final-1920 screenshots are historical, superseded evidence.

Desktop screenshots include the hardware cursor (-C), unlike the earlier window-only test that missed the duplicate. See validation.json, single-cursor-mouse.json, cursor-outside-game.png, single-cursor-return.png, selected-resolution-inventory.png and final-1920-paused.png. All four HUD edges, inventory and pause controls are visible. Held left/right mouse movement remains absolute; middle-button movement hides the pointer and release restores it. App switching restores the ordinary Mac pointer; returning to the game shows one correctly positioned arrow. Normal launcher cold start loaded the helper, confirmed by the process's open-file map.

Object detail remains 1.0 (100%) and DXVK cap remains 120 FPS. The existing manual saves in the pre-test snapshot are unchanged. The user selected a newer TestQ session while testing; never replace that progress with the private Test profiling save. The backup user-data directory is for recovery, not an instruction to overwrite newer user progress.

Historical CPU-performance benchmarks used an 800×600 client. Current 1280×800 gameplay with 1512×982 renderer output presents a different view/UI workload; fullscreen screenshot FPS readings are smoke checks, not controlled comparisons or a claim of sustained 110 FPS.

## Rejected trials

Forcing fullscreen while the game reports windowed stayed windowed. An unforced renderer output switched the Mac display mode before Wine resized its native window, recreating clipping; reverted. Removing the native-arrow ShowCursor repair removed the correctly scaled arrow and left the wrong unscaled pointer; that candidate was not installed. The final EXE retains the original ShowCursor behavior. The temporary width=800 height=600 debugging flags were removed after the user's resolution report.

## Recovery

Pre-change DSLOA.exe, dgVoodoo.conf, production-before-Info.plist and support-before-static-manifest.json/static-patches.json/README.md are in this directory. To restore the preceding windowed build, stop only this Wine prefix, restore those matching game/config/manifest files and the wrapper plist, then run check-install.py. The private fullscreen-cursor.dylib becomes inactive when the previous plist is restored. Do not restore the stale virtual-desktop setting or overwrite any saves. Production registry and user-data backups are also retained here as evidence.

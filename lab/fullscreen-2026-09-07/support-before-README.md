# Dungeon Siege Optimized

Open [Dungeon Siege Optimized.app](<~/Applications/Dungeon Siege Optimized.app>) and choose Continue (`Test OP`).

The latest object-transform change combines three submissions and caches unchanged calculations. Two settled runs per build averaged 91.94 to 95.68 FPS (about 4.1%). Object detail stays at 100%, and the presentation cap is 120 FPS. Dense forest views still fall below 110 FPS. Normal startup and protected files were checked, then the game and tests were closed at your request.

The retained native cursor fix skips the old software-cursor background copies that were blocking the renderer. In the cursor-fix tests, two repeat forest walks had no frames over 80 ms; worst frame time fell from 119 ms to 53/46 ms. Average CPU frame cadence was 82–84 FPS versus 80 before. Smaller spikes and slower dense views remain; these are tested-route results, not a whole-game guarantee.

The earlier normal-transform optimization moves repeated floating-point setup outside the inner loop. Two settled dense-view runs per build averaged 90.93 to 93.72 FPS (about 3.1%) with unchanged graphics settings. 14,400 complete-loop comparisons matched all output bits. Walking remained around 82–84 FPS; one 87 ms hitch remained in the repeat. This is an incremental dense-view gain, not a claim that all movement stutter is fixed.

Earlier math gains, the corrected held-click behavior and OP mods remain. Only the used attack school gains school XP; the main attribute grows at 1.35 and the others at 1.0. Rare/unique loot and vendor changes are installed. The original save is preserved separately; Continue uses its migrated OP copy.

Progress is stored in `user-data/Dungeon Siege LOA/Save` here. The original app and original saves remain separate. The native arrow replaces game cursor artwork; middle-button camera movement hides it and release restores it.

`static-manifest.json` pins five binaries; `static-patches.json` records 23 jump hooks plus one direct patch. Normal startup contains no profiler or diagnostic lock hooks. Keep `~/Applications/Dungeon Siege Wine10 Test.app`, which supplies the engine. The previous build is backed up under the experiment folder's `phase9/release-before`.

[Detailed results and source](<~/Documents/Dungeon Siege 1/experiments/2026-09-06/STATUS.md>) · [Mod details](<~/Documents/Dungeon Siege 1/mods/2026-09-06/README.md>)

[Exact mathematical changes and measured gains](<~/Documents/Dungeon Siege 1/experiments/2026-09-06/phase9/MATH-AND-PERFORMANCE.md>)

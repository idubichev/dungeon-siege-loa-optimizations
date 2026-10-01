# Phase 5 — native arrow and release installation

The uninstrumented `08-arrow-triangle/DSLOA.exe` is installed in the normal Optimized/Wine10 launcher. See `../STATUS.md` for current measurements, preservation and limitations.

- `installed-release.json`: final hash, installation and backup location.
- `08-arrow-triangle/validation.json`: 180,000 final-EXE comparisons passed.
- `15-release-light/`: 95.66 FPS five-sample mean; inventory, movement and cursor smoke captures.
- `16-normal-launch/`: actual launcher/current save smoke, 94.1 FPS active capture, then paused; protected files unchanged.
- `12-arrow-rotated/`: 87.61 FPS CPU frame cadence, still below stable90 target.
- `13-draw-profile/` and `14-draw-rotated/`: diagnostic only, overhead present, not installed.
- `cursor-focus.m` / dylib and folders04–06: rejected custom-art focus experiments; never installed in normal launcher. The standard arrow avoids that custom cursor presentation path.
- `release-before/`: prior release backup. `release-protected-files.json`: original EXE and both original/optimized save pairs.

Input testing uses Wine SendInput and explicitly authorized macOS focus/screenshots, without terminal injection or Accessibility permission changes. No normal launch needs these test helpers.

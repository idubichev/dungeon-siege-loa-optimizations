# UI and physical mouse correction — accepted and installed

The user reported tiny/degraded text and physical mouse clipping at 1920×1080. Earlier SetCursorPos tests did not prove physical movement; native event helpers did not move the pointer and are invalid evidence.

The private 1280×800 UI trial retained dgVoodoo 1512×982 rendering/presentation. The user physically tested it and confirmed "Hey you did it!!". This UI setting enlarges text/layout 50% horizontally and 35% vertically versus 1920×1080. Production was restored from minimization through ShowWindow, then its resolution was changed using the in-game options. The current Testq session was preserved in Testq (0-05-36).dssave. Both normal INIs now persist 1280×800; the user-data INI was made writable so future choices can persist. All renderer binaries, output resolution, full-detail setting and 120 FPS cap remain unchanged.

The expanded inventory task subsequently cold-started the normal launcher with this configuration. See ../../../../mods/2026-09-07-inventory/validation.json for save and deployment evidence. Never replace Testq progress with old private profiling saves.

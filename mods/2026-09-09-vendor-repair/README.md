# Vendor repair v3

The user reported that v2 removed all generated merchant stock and retained only buybacks. The 24 offline tests used a stub for the generator, so they did not validate live item creation. Treat v2 as failed in game.

The prior helper called the initialization stock wrapper at 0x57d6fa, which passes zero for the live/synchronized creation argument to 0x57c997. The new helper reproduces the tab traversal but passes one, selecting SCloneGo rather than the direct construction path in 0x57d765. This is the repair hypothesis, not an independently confirmed root cause.

Replacements are generated before deleting any old inventory. A second native inventory listing must contain more items than the original snapshot; otherwise old inventory is retained. Original buyback-map and equipped-item exclusions remain. No party inventory or save file is edited. If an individual old-item removal fails, the loop stops; newly generated and remaining old items are retained.

Magic uses the existing game query syntax -mod(1). Jonn's 196 requested rolls are 69 magic, 60 rare, 32 unique and 35 ordinary. Power budgets and quantities are unchanged. These are requests, not guaranteed resulting item counts. All 181 modified store definitions retain prior non-store text and combined monster loot edits.

Verification: 313 archive CRC checks, unchanged 181 stock budgets, 26 emulated helper cases including no-generation preservation, register/stack preservation and live-generation arguments. The generator itself is still instrumented, not executed in these offline cases. Installed executable byte differences compared with the pre-vendor optimized executable are restricted to the three declared ranges, preserving other optimizations, XP and companion patches.

Installed successfully and launcher validator passed. Game relaunched through CUA. The optimized app and wrapper both timed out when acquiring desktop control, so no shop interaction, visible stock, repeated reroll or save/reload has been validated. User needs to open/close/reopen Jonn to check the live result. Do not report this as confirmed fixed until then.

Backups of the prior v2 executable, archive and manifests are in backup/. The known pre-reroll backup remains in ../2026-09-09-vendors/backup/. All game saves remain untouched.

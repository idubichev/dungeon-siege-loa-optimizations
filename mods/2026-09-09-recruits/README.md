# Ehb companion recruitment bonus

Installed September 9, 2026, while Dungeon Siege was closed. Relaunch **Dungeon Siege Optimized** to activate.

The 16 Ehb companions receive +2 natural Strength, +2 natural Dexterity and +2 natural Intelligence on their next successful recruitment, once per companion per saved campaign. Existing party members receive no automatic grant. A previously hired companion can receive their first grant if recruited again after installation; further rehires cannot stack it. Loading a save from before a grant also restores the pre-grant stats and marker.

The change runs inside the existing successful-hire conversation branch, rather than changing spawn templates. It is intended to cover NPCs already present in a saved world. The existing GameAuditor database stores the one-time marker. No save files were edited. Save/reload and recruitment have not yet been tested in-game.

Covered: Andiemus, Boryev, Gloern, Goquua, Gyorn, Kroduk, Lord Bolingar, Merik, Naidi, Phaedriel, Rhut, Rusk, Sikra, Ulfgrim, Ulora and Zed. LoA and Utraean recruitment scripts are outside this package's scope.

## Implementation

- `DS_Companion_Bonus.dsres` overrides the 16 effective original recruitment scripts, adding only a guarded block in each acceptance branch.
- Each block calls `Rules.RCSetNaturalSkillLevel` for the three attributes using a private -1002.0 request.
- A paired 36-byte native helper intercepts the Rules setter's call at `0x5b9377`. Only that exact private request becomes `current raw level + 2`; every ordinary argument passes through unchanged.
- The original setter at `0x5b9690` remains intact and updates the natural level, XP and next-level threshold using the game's existing routines and limits.
- Natural skill level at `+0x30` is used directly. Modified level at `+0x34` and starting level at `+0x38` are not read into the bonus, avoiding duplicate equipment or starting-stat awards. Fractional natural levels are retained.
- Trained attack-school levels and equipment are unchanged. The bonus causes no recurring AI update loop.

The EXE and resource are a pair; do not install either independently. Existing performance, fullscreen, cursor, combat-XP, loot and inventory modifications are preserved. The install manifest now pins the new archive as well as the paired EXE.

## Verification and limitations

`validation.json` records 72 offline x86 emulation cases across natural levels, ordinary/negative/private arguments and two load addresses. Register preservation, flags, return address, x87 stack balance, and independence from modified/starting stats passed. All 16 archive CRC/source checks and Skrit brace checks passed. Only the call, unused code padding and section virtual size changed in the EXE.

This is not an in-game or Skrit-compiler test. Successful hiring, UI refresh and save/reload behavior still need gameplay confirmation. `installed.json` records successful installation, and the optimized launcher's complete hash check passed.

## Files and rollback

`build.py`, `verify.py` and `install.py` reproduce the work against the pinned pre-change build. `original/` and `source/` contain the original and modified scripts. `patch.json` records source archive provenance, hashes, marker names and machine code.

To roll back while the game is closed, restore `backup/DSLOA.exe` to the game folder, restore both JSON files from `backup/` to the optimized support folder, and remove `DSLOA/DS_Companion_Bonus.dsres`. These backups retain the 135% combat-XP patch. Already saved attribute grants remain in the character's saved natural stats; undoing those would require a pre-grant save. Never mix the original executable with this resource archive.

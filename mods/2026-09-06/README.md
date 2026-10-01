# Dungeon Siege OP loot, vendors and attributes

Installed in the optimized Legends of Aranna game. Open **Dungeon Siege Optimized.app**, then **Continue** to load **Test OP**. This is a copy of `Test (0-04-34).dssave` with the same progress, inventory, levels and XP. The original save remains available.

## Rules

- Only the attack school used receives its normal school XP.
- All three attributes grow from that attack: the main attribute uses **1.35**, the other two use **1.0**. Main attributes are Strength for melee, Dexterity for ranged, and Intelligence for either magic school.
- Eligible rare-item rolls are multiplied by 10 and unique-item rolls by 5, capped by each roll's probability budget.
- Vendors replace up to three existing eligible stock rolls with two rare rolls and one unique roll. Existing potion and resurrection-scroll supply rolls are increased within stock budgets. Stock totals are retained.

The two packages are `DS_OP_Attributes_v1.dsres` and `DS_OP_LootVendors_v1.dsres`, in the optimized game's `DSLOA` folder. Loot and vendors share one package to avoid conflicting full-file overrides. Existing ikkyo vendor template changes are retained.

Already spawned creatures and saved shop inventories may need new spawning/restocking before their loot or stock changes. A vendor visit has not yet been verified visually.

## Verification and save handling

All 310 packaged resources passed archive CRC and structural checks. The formula changes are limited to the 12 attribute influences. A private in-game melee kill awarded 6 melee XP and zero XP to the other schools; Strength growth was 1.35 times the equal Dexterity/Intelligence growth, within save rounding. Evidence is in `build/validation.json` and `build/xp-playtest-migrated.json`.

Saved characters retain attribute coefficients in `world.xdat`, so the resource package alone does not update an existing save. `migrate_save.py` creates a separate save with only those serialized coefficients changed. It preserves all other archive members and verifies the exact changed bytes. The installed save's migration report sits next to `Test OP.dssave`.

To return to the pre-mod state, close the game, move these two packages out of `DSLOA`, and load the preserved original save. Removing the packages alone does not reverse attribute growth already earned or coefficients serialized in a modded save. Private experiment saves, including the invincible travel-test character, are not installed in the normal game.

Source and the complete change list are in `build_mods.py`, `migrate_save.py`, and `build/manifest.json`. The normal save backup and binary rollback are under `../../experiments/2026-09-06/phase6/`.

## Later combat XP update — 2026-09-09

A separate native patch now scales damage-based combat XP to 135% on the next launch. The formulas in this resource package remain unchanged; attribute growth applies to the boosted award. This does not multiply support casting or scripted quest rewards. See `../2026-09-09-xp135/README.md` for scope, validation and rollback.

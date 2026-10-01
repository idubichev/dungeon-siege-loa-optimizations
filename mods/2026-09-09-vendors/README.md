# Vendor stock v2 and reroll on shop exit

Built for the current optimized DS1/LoA executable on September 9, 2026. Installation status is recorded in `installed.json`.

## Stock fix

The old builder selected only one equipment group per tab and omitted the `melee` and `ranged` categories entirely. Stonebridge's Jonn consequently had only six enhanced rolls among 196 equipment rolls, with all weapons unchanged.

Version 2 updates each eligible equipment bucket, including melee, ranged, body armor, gloves, boots, helmets and shields. Half the minimum quantity targets rare items, and one quarter targets unique items, rounded down; the remainder stays normal. Quantities and power ranges stay the same. Small buckets therefore have a lower special-item share. Existing special rolls and supply restocks are retained.

Jonn now has 97 rare-targeted, 42 unique-targeted and 57 ordinary rolls, totaling the same 196. These are requests to the game's generator, not a guarantee of 139 distinct special items: actual results still depend on available templates, modifiers and inventory capacity. His seven equipment categories are all covered. There are 181 updated vendor definitions across the installed content.

The existing combined loot/vendor archive is replaced under its original installed filename, `DSLOA/DS_OP_LootVendors_v1.dsres`, avoiding equal-priority duplicate overrides. Its internal title identifies v2. Monster loot edits and all content outside the replaced `store_pcontent` blocks are preserved.

## Reroll

After the last shopper exits, the new native helper reads the merchant's current `store_pcontent`, removes unequipped shop stock, and invokes the game's stock generator again. The next shop visit sees the new selection. Merchants without stock definitions, including hire-only stores, are skipped.

Items in the native sold-item/buyback map are retained. Equipped merchant items are retained. Party inventories are not traversed or changed. If a stock removal fails, regeneration is aborted rather than adding duplicate stock. There is no recurring timer or gameplay-frame hook.

This supports refreshing a previously saved shop on its next close; no save migration is performed. After relaunching, open and close the shop once, then reopen it to replace old saved stock.

## Implementation and validation

The native patch replaces the five-byte vector-erase call at `0x5e52f8`, within `GoStore::RSRemoveShopper`, with a call to a 322-byte helper at `0xc15460`. The original erase runs first. A remaining-shopper check prevents refresh while another shopper remains. The code uses relative calls and existing executable padding; no import, base-relocation, performance-hook, XP-hook or companion-hook changes are needed.

`verify.py` checks all 313 archive CRCs, unchanged stock quantity budgets, unchanged text outside vendor blocks, and Stonebridge category coverage. It emulates the actual hook for 24 scenarios/load-address combinations with instrumented engine callees, including buyback/equipped preservation, absent stock, multiple shoppers and failed removal. Registers, stack and flags are checked.

These are offline checks, not full engine integration. In-game stock generation, repeated rerolls and save/reload still need confirmation. Intended use is this single-player install; multiplayer has not been tested.

## Rollback

While the game is closed, restore `backup/DSLOA.exe` and `backup/DS_OP_LootVendors_v1.dsres` to their game locations, and restore the two backed-up JSON manifests to the optimized support directory. These backups include the 135% combat-XP and companion bonuses. Existing saves are not changed by installation or rollback.

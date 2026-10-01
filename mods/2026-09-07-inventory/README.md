# Expanded inventory — installed 7 September 2026

Zhixalom’s Inventory v3.2, 1024×768 LoA SinglePlayer variant, downloaded unchanged from the author:
https://www.zhixalom.com/lair/2004/08/31/zhixaloms-inventory-v3-2/

The character grid is 11×22 = 242 squares (original 13×4 = 52): about 4.65 times the space. Backpacks have 12×21 = 252 squares. Pack animals and shop/trade layouts are also expanded. The package changes seven UI/default resources, including a 2.1 billion gold cap. No files overlap the two OP resource packages; all performance binaries are unchanged.

Installed in the optimized game's DSLOA directory and pinned by the startup hash manifest. Open Dungeon Siege Optimized.app, Continue, then I for inventory. Keep gameplay UI at 1280×800: the mod requires at least 1024×768. The underlying dgVoodoo render/presentation target stays 1512×982, full object detail and 120 FPS cap remain.

## Existing-save verification

The current Testq session was saved normally as Testq (0-05-36).dssave before restarting; its complete user-data folder was backed up in user-data-before. An exact copy was loaded in the isolated Profile installation with this mod. A mana potion was placed in column 11, row 22, saved normally, then recovered visibly after terminating and restarting the game. The serialized position was (575,702), beyond the original four-row inventory. The potion could be picked up again. All item templates, XP and levels, and 37 gold were preserved. See validation.json and last-slot-after-restart.png.

Production uses the original untouched Testq save, not the private test result. All four manual saves matched their backup hashes at installation. No save conversion or new character is required for the tested save. Shop and pack-animal changes were inspected in the resources, not playtested at a merchant.

## Recovery and limitations

This is the single-player variant. Dungeon Siege multiplayer character saves have a 255-item limit; do not use this large single-player configuration for multiplayer characters.

Before removing the mod, move every item into the original inventory space and save, or load a preserved pre-mod save. Simply removing an inventory mod while extra cells contain items risks inaccessible items. To remove it, close the optimized game, move its ZhixalomsInv32_1024x768_LOA_SinglePlayer.dsres out of DSLOA, and remove the matching DSLOA entry from static-manifest.json (or restore static-manifest-before.json if no later changes have been made). Keep the original saves and performance files.

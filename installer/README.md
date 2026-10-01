# Dungeon Siege Installer

The Mac app players download from Releases. One window, one button:

1. Finds the game: the GOG offline installer in Downloads, or an existing GOG/Steam install (Wine wrappers, CrossOver, Whisky, or a folder copied from a PC).
2. Finds `Legends of Aranna fix.zip` in Downloads, or offers to open its download page.
3. Downloads Wine 10 (Sikarugir build), Sikarugir's wrapper libraries, dgVoodoo 2.53 and DXVK-macOS 1.10.3, each checked by SHA-256 against [`patches/manifest.json`](../patches/manifest.json).
4. Builds `~/Applications/Dungeon Siege LoA.app` with its own launcher script (Sikarugir's launcher breaks DirectDraw's cooperative level for this game, so it isn't used), creates the Wine prefix, keeps user folders inside the app, and runs GOG's installer silently (retrying if its first pass stops after DirectX).
5. Layers the Legends of Aranna fix on top, installs the renderer DLLs and Wine DLL overrides, and applies the BPS patches with output hash checks.

Build: `./build.sh` (needs the Xcode Command Line Tools). It produces a universal, ad-hoc signed app and `build/Dungeon-Siege-Installer.zip`.

Command-line use, for testing:

```sh
"Dungeon Siege Installer.app/Contents/MacOS/Dungeon Siege Installer" --detect
"Dungeon Siege Installer.app/Contents/MacOS/Dungeon Siege Installer" \
  --install <setup_dungeon_siege_1….exe or game folder> --loa <Legends of Aranna fix.zip> [--to <path/Name.app>]
```

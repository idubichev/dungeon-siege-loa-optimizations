#!/usr/bin/env python3
"""Patch Dungeon Siege: Legends of Aranna with the SSE performance build.

Easiest: double-click Install.command, or run "python3 patch.py --install-renderer
--install-dxvk" with no folder. The patcher then finds the game by itself.

Example game folder (a Sikarugir wrapper named "Dungeon Siege"):
    ~/"Applications/Sikarugir/Dungeon Siege.app/Contents/SharedSupport/prefix/drive_c/GOG Games/Dungeon Siege"

    python3 patch.py "/path/to/Dungeon Siege"                    patch the game
    python3 patch.py "/path/to/Dungeon Siege" --install-renderer download dgVoodoo 2.53 first
    python3 patch.py "/path/to/Dungeon Siege" --install-dxvk     also install DXVK for macOS
    python3 patch.py "/path/to/Dungeon Siege" --status           show what is installed
    python3 patch.py "/path/to/Dungeon Siege" --restore          put the original files back

Every file is checked by SHA-256 before and after it is written. Originals are
copied to "dspatch-backup" inside the game folder the first time they change.
"""
import argparse
import hashlib
import io
import json
import shutil
import subprocess
import time
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import bps  # noqa: E402

MANIFEST = json.loads((ROOT / "patches" / "manifest.json").read_text())
BACKUP = "dspatch-backup"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def find(folder, name):
    """Case-insensitive lookup; Wine prefixes keep the installer's casing."""
    for entry in folder.iterdir():
        if entry.name.lower() == name.lower():
            return entry
    return folder / name


def backup(folder, path):
    store = folder / BACKUP
    store.mkdir(exist_ok=True)
    saved = store / path.name
    if path.is_file() and not saved.exists():
        shutil.copy2(path, saved)


def download(url, expected):
    print(f"  downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != expected:
        sys.exit(f"  download checksum mismatch for {url}; nothing was changed")
    return data


SEARCH = [
    "Applications/Sikarugir/*.app/Contents/SharedSupport/prefix/drive_c/*/Dungeon Siege*",
    "Applications/Wineskin/*.app/Contents/SharedSupport/prefix/drive_c/*/Dungeon Siege*",
    "Applications/*.app/Contents/SharedSupport/prefix/drive_c/*/Dungeon Siege*",
    "Library/Application Support/CrossOver/Bottles/*/drive_c/*/Dungeon Siege*",
]
OVERRIDES = ["ddraw", "d3dim", "d3d8", "d3d11", "d3d10core"]


def find_games():
    found = []
    for pattern in SEARCH:
        for match in sorted(Path.home().glob(pattern)) + sorted(Path("/").glob(pattern)):
            if match.is_dir() and find(match, "DSLOA.exe").is_file() and match not in found:
                found.append(match)
    return found


def choose_game():
    games = find_games()
    if len(games) == 1:
        print(f"Found the game in {games[0]}")
        return games[0]
    if games:
        print("Found more than one Dungeon Siege install:")
        for i, g in enumerate(games, 1):
            print(f"  {i}. {g}")
        pick = input("Type the number of the one to patch and press Return: ").strip()
        if not pick.isdigit() or not 1 <= int(pick) <= len(games):
            sys.exit("No install chosen; nothing was changed.")
        return games[int(pick) - 1]
    print("Couldn't find Dungeon Siege automatically.")
    typed = input("Drag your Dungeon Siege folder (the one with DSLOA.exe) into this window, then press Return: ")
    return Path(typed.strip().strip("'\"").replace("\\ ", " ")).expanduser()


def wine_settings(folder):
    """Set Wine to load the renderer DLLs from the game folder (the winecfg step)."""
    prefix = next((p for p in folder.parents if (p / "user.reg").is_file() and (p / "drive_c").is_dir()), None)
    if prefix is None:
        print("Wine settings: no Wine prefix found above the game folder. Set the DLL overrides\n"
              "by hand (INSTALL.md, step 3).")
        return
    if subprocess.run(["pgrep", "-x", "wineserver"], capture_output=True).returncode == 0:
        sys.exit("Wine is running. Quit Dungeon Siege and any other Wine apps, then run this again.")
    reg = prefix / "user.reg"
    text = reg.read_text(encoding="utf-8", errors="surrogateescape")
    lines = text.split("\n")
    header = next((i for i, l in enumerate(lines) if l.startswith("[Software\\\\Wine\\\\DllOverrides]")), None)
    if header is None:
        stamp = int(time.time())
        lines += [f"[Software\\\\Wine\\\\DllOverrides] {stamp}",
                  f"#time={(stamp + 11644473600) * 10**7:x}", ""]
        header = len(lines) - 3
    end = next((i for i in range(header + 1, len(lines)) if lines[i].startswith("[")), len(lines))
    changed = False
    for name in OVERRIDES:
        entry = f'"{name}"="native,builtin"'
        at = next((i for i in range(header + 1, end) if lines[i].startswith(f'"{name}"=')), None)
        if at is None:
            insert = header + 1
            while insert < end and lines[insert].startswith("#"):
                insert += 1
            lines.insert(insert, entry)
            end += 1
            changed = True
        elif lines[at] != entry:
            lines[at] = entry
            changed = True
    if not changed:
        print("  Wine DLL settings already correct")
        return
    saved = prefix / "user.reg.dspatch-backup"
    if not saved.exists():
        shutil.copy2(reg, saved)
    reg.write_text("\n".join(lines), encoding="utf-8", errors="surrogateescape")
    print("  set Wine to load ddraw, d3dim, d3d8, d3d11 and d3d10core from the game folder")


def install(folder, files):
    """files: {name: (bytes, expected_sha256)}"""
    for name, (data, expected) in files.items():
        if hashlib.sha256(data).hexdigest() != expected:
            sys.exit(f"  {name} from the download is not the expected build; nothing was changed")
    for name, (data, _) in files.items():
        target = find(folder, name)
        backup(folder, target)
        target.write_bytes(data)
        print(f"  installed {target.name}")


def install_renderer(folder):
    r = MANIFEST["renderer"]["dgvoodoo"]
    print(f"dgVoodoo {r['version']}")
    archive = zipfile.ZipFile(io.BytesIO(download(r["url"], r["sha256"])))
    install(folder, {name: (archive.read(member), digest)
                     for name, (member, digest) in r["files"].items()})


def install_dxvk(folder):
    r = MANIFEST["renderer"]["dxvk"]
    print(f"DXVK-macOS {r['version']}")
    archive = tarfile.open(fileobj=io.BytesIO(download(r["url"], r["sha256"])))
    install(folder, {name: (archive.extractfile(member).read(), digest)
                     for name, (member, digest) in r["files"].items()})
    conf = find(folder, "dxvk.conf")
    backup(folder, conf)
    shutil.copyfile(ROOT / "config" / "dxvk.conf", conf)
    print(f"  installed {conf.name}")


def state(folder, name):
    entry = MANIFEST["files"][name]
    digest = sha256(find(folder, name))
    if digest == entry["original"]:
        return "original"
    if digest == entry["patched"]:
        return "patched"
    return "missing" if digest is None else "unknown"


def status(folder):
    print(f"Game folder: {folder}")
    for name in MANIFEST["files"]:
        print(f"  {name:<12} {state(folder, name)}")
    for name, digest in MANIFEST["requires"].items():
        ok = sha256(find(folder, name)) == digest
        print(f"  {name:<12} {'dgVoodoo 2.53' if ok else 'not dgVoodoo 2.53'}")


def patch(folder, force):
    for name, digest in MANIFEST["requires"].items():
        if sha256(find(folder, name)) != digest and not force:
            sys.exit(f"{name} is not dgVoodoo 2.53. The patched game reads dgVoodoo 2.53's\n"
                     "internal state, so it needs exactly that build. Run again with\n"
                     "--install-renderer to download it, or see INSTALL.md.")
    states = {name: state(folder, name) for name in MANIFEST["files"]}
    for name, s in states.items():
        if s in ("missing", "unknown"):
            sys.exit(f"{name} is {s}. This patch needs DSLOA.exe from the community \"Legends of Aranna fix\"\n"
                     f"(SHA-256 {MANIFEST['files']['DSLOA.exe']['original']}), installed over the GOG or Steam game.\n"
                     "If another mod changed DSLOA.exe, restore the original first.")
    for name, s in states.items():
        path = find(folder, name)
        if s == "patched":
            print(f"  {path.name} already patched")
            continue
        entry = MANIFEST["files"][name]
        result = bps.apply(path.read_bytes(), (ROOT / "patches" / entry["patch"]).read_bytes())
        if hashlib.sha256(result).hexdigest() != entry["patched"]:
            sys.exit(f"  {path.name}: patched output did not verify; nothing was written")
        backup(folder, path)
        path.write_bytes(result)
        print(f"  patched {path.name}")
    print("Done. Launch DSLOA.exe as usual.")


def restore(folder):
    store = folder / BACKUP
    if not store.is_dir():
        sys.exit("No backup folder found; nothing to restore.")
    for saved in sorted(store.iterdir()):
        shutil.copy2(saved, find(folder, saved.name))
        print(f"  restored {saved.name}")
    print(f"Originals restored. {store} was left in place.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("game", nargs="?", help="the Dungeon Siege folder (the one containing DSLOA.exe); found automatically if left out")
    parser.add_argument("--install-renderer", action="store_true", help="download and install dgVoodoo 2.53 first")
    parser.add_argument("--install-dxvk", action="store_true", help="download and install DXVK-macOS 1.10.3 and dxvk.conf")
    parser.add_argument("--status", action="store_true", help="report what is installed and exit")
    parser.add_argument("--restore", action="store_true", help="restore the original files from the backup")
    parser.add_argument("--force", action="store_true", help="patch even if dgVoodoo 2.53 is not detected (not recommended)")
    args = parser.parse_args()

    folder = Path(args.game).expanduser() if args.game else choose_game()
    if folder.is_file():
        folder = folder.parent
    if not find(folder, "DSLOA.exe").is_file():
        sys.exit(f"DSLOA.exe not found in {folder}")

    if args.status:
        return status(folder)
    if args.restore:
        return restore(folder)
    if args.install_renderer:
        install_renderer(folder)
    if args.install_dxvk:
        install_dxvk(folder)
    if args.install_renderer or args.install_dxvk:
        wine_settings(folder)
    print("Dungeon Siege performance patch")
    patch(folder, args.force)


if __name__ == "__main__":
    main()
